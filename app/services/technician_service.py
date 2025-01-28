# app/services/technician_service.py

from datetime import datetime, timedelta
from sqlalchemy import text
from app import db

def get_all_inventory_items():
    """
    Returns all items from InventoryItems with their category info, etc.
    """
    query = text("""
        SELECT i.item_id,
               i.name,
               i.quantity,
               i.reorder_level,
               i.expiration_date,
               c.category_name
        FROM InventoryItems i
        JOIN InventoryCategories c ON i.category_id = c.category_id
        ORDER BY i.name ASC
    """)
    return db.session.execute(query).fetchall()


def update_inventory_item(item_id, new_quantity, performed_by):
    """
    Updates an item's quantity in the database.
    Also logs the action in InventoryLogs.
    If quantity < reorder_level, create a low-stock task for technicians.
    """
    try:
        # 1) Fetch the item’s current data
        fetch_sql = text("""
            SELECT item_id, name, quantity, reorder_level
            FROM InventoryItems
            WHERE item_id = :item_id
        """)
        row = db.session.execute(fetch_sql, {"item_id": item_id}).fetchone()
        if not row:
            return {"error": f"Item with ID {item_id} not found."}, 404

        old_qty = row.quantity
        reorder_lvl = row.reorder_level
        item_name = row.name

        # 2) Update the quantity
        update_sql = text("""
            UPDATE InventoryItems
            SET quantity = :new_qty,
                updated_at = CURRENT_TIMESTAMP
            WHERE item_id = :item_id
        """)
        db.session.execute(update_sql, {
            "new_qty": new_quantity,
            "item_id": item_id
        })

        # 3) Log into InventoryLogs
        quantity_change = new_quantity - old_qty
        action = "restocked" if quantity_change >= 0 else "expired"
        insert_log_sql = text("""
            INSERT INTO InventoryLogs (item_id, action, quantity_change, performed_by)
            VALUES (:item_id, :action, :qty_change, :user_id)
        """)
        db.session.execute(insert_log_sql, {
            "item_id": item_id,
            "action": action,
            "qty_change": quantity_change,
            "user_id": performed_by
        })

        # 4) If new_qty < reorder_level => create a "low stock" task for technicians
        if new_quantity < reorder_lvl:
            _create_low_stock_task_for_techs(item_name, item_id, reorder_lvl, new_quantity)

        db.session.commit()
        return {"message": "Inventory updated successfully!"}, 200

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def _create_low_stock_task_for_techs(item_name, item_id, reorder_level, current_qty):
    """
    Helper function that inserts a new "low stock" task in the 'Tasks' table,
    assigned to all technicians.
    """
    # 1) Fetch all technicians
    technicians_sql = text("""
        SELECT user_id
        FROM Users
        WHERE role = 'technician'
    """)
    tech_rows = db.session.execute(technicians_sql).fetchall()
    if not tech_rows:
        return  # no technicians to assign the task

    # 2) Insert the task in 'Tasks'
    task_sql = text("""
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
    """)
    description_text = (f"Item '{item_name}' is below reorder level! Current qty: {current_qty}, "
                        f"reorder level: {reorder_level}. Refill needed.")
    res = db.session.execute(task_sql, {
        "t_name": f"LOW STOCK - {item_name}",
        "t_desc": description_text,
        "due_date": datetime.now().strftime('%Y-%m-%d')  # or set a more suitable date
    })
    new_task_id = res.fetchone()[0]

    # 3) Insert into TaskAssignments for each technician
    assign_sql = text("""
        INSERT INTO TaskAssignments (task_id, user_id)
        VALUES (:tid, :uid)
    """)
    for row in tech_rows:
        db.session.execute(assign_sql, {
            "tid": new_task_id,
            "uid": row.user_id
        })
