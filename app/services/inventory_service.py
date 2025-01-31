from datetime import datetime

from sqlalchemy import text

from app import db


def get_all_inventory_items():
    items_query = text(
        """
        SELECT i.item_id, i.name, i.reorder_level, i.category_id, c.category_name
        FROM InventoryItems i
        JOIN InventoryCategories c ON i.category_id = c.category_id
        ORDER BY i.name ASC
    """
    )
    items = db.session.execute(items_query).fetchall()

    batch_query = text(
        """
        SELECT item_id, expiration_date, quantity
        FROM InventoryBatches
        ORDER BY expiration_date ASC
    """
    )
    batches = db.session.execute(batch_query).fetchall()

    # Group batches by item_id and calculate total quantity
    batch_dict = {}
    for b in batches:
        if b.item_id not in batch_dict:
            batch_dict[b.item_id] = {
                "batches": [],
                "total_qty": 0,
                "has_real_expiry": False,
            }

        batch_dict[b.item_id]["batches"].append(
            {"expiration_date": b.expiration_date, "quantity": b.quantity}
        )

        batch_dict[b.item_id]["total_qty"] += b.quantity

        # Mark if the batch has a real expiry date
        if str(b.expiration_date)[:10] != "9999-12-31":
            batch_dict[b.item_id]["has_real_expiry"] = True

    # Combine item + list of its batches and total quantity
    formatted_items = []
    for row in items:
        formatted_items.append(
            {
                "item": {
                    "item_id": row.item_id,
                    "name": row.name,
                    "reorder_level": row.reorder_level,
                    "category_name": row.category_name,
                },
                "batches": batch_dict.get(row.item_id, {}).get("batches", []),
                "total_qty": batch_dict.get(row.item_id, {}).get("total_qty", 0),
                "has_real_expiry": batch_dict.get(row.item_id, {}).get(
                    "has_real_expiry", False
                ),
            }
        )

    return formatted_items


def update_inventory_item(item_id, new_quantity, performed_by, expiration_date=None):
    """
    Calls the 'update_inventory' PostgreSQL function to add or replace
    a batch. If expiration_date is None or '9999-12-31', it merges into
    the single "no expiry" row. Otherwise it merges into that date row.
    """
    try:
        query = text(
            """
            SELECT update_inventory(
                :item_id,
                :new_quantity,
                :performed_by,
                :expiration_date
            ) AS result;
        """
        )

        result = db.session.execute(
            query,
            {
                "item_id": item_id,
                "new_quantity": new_quantity,
                "performed_by": performed_by,
                "expiration_date": expiration_date or None,
            },
        ).fetchone()

        db.session.commit()

        if result and result.result == "Inventory updated successfully":
            return {"message": "Inventory updated successfully"}, 200
        else:
            return {"error": "Inventory update failed"}, 400

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def _create_low_stock_task_for_techs(item_name, item_id, reorder_level, current_qty):
    """
    Helper function that inserts a new "low stock" task in the 'Tasks' table,
    assigned to all technicians.
    """
    technicians_sql = text(
        """
        SELECT user_id
        FROM Users
        WHERE role = 'technician'
    """
    )
    tech_rows = db.session.execute(technicians_sql).fetchall()
    if not tech_rows:
        return  # no technicians to assign the task

    task_sql = text(
        """
        INSERT INTO Tasks (
            task_name, task_description, due_date,
            task_type_id, priority, created_by
        )
        VALUES (
            :t_name, :t_desc, :due_date,
            1,  -- or some 'task_type_id' for "Low Stock"
            'high',
            0   -- created_by = 0 => system?
        )
        RETURNING task_id
    """
    )
    description_text = (
        f"Item '{item_name}' is below reorder level! "
        f"Current qty: {current_qty}, reorder level: {reorder_level}."
    )
    res = db.session.execute(
        task_sql,
        {
            "t_name": f"LOW STOCK - {item_name}",
            "t_desc": description_text,
            "due_date": datetime.now().strftime("%Y-%m-%d"),
        },
    )
    new_task_id = res.fetchone()[0]

    assign_sql = text(
        """
        INSERT INTO TaskAssignments (task_id, user_id)
        VALUES (:tid, :uid)
    """
    )
    for row in tech_rows:
        db.session.execute(assign_sql, {"tid": new_task_id, "uid": row.user_id})
