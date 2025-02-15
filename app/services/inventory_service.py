from datetime import datetime
from sqlalchemy import text
from app import db


def get_all_inventory_items():
    items_query = text("""
        SELECT i.item_id, i.name, i.reorder_level, i.category_id, c.category_name
        FROM InventoryItems i
        JOIN InventoryCategories c ON i.category_id = c.category_id
        ORDER BY i.name ASC
    """)
    items = db.session.execute(items_query).fetchall()

    batch_query = text("""
        SELECT item_id, expiration_date, quantity
        FROM InventoryBatches
        ORDER BY expiration_date ASC
    """)
    batches = db.session.execute(batch_query).fetchall()

    # Group batches by item_id and calculate total quantity
    batch_dict = {}
    for b in batches:
        if b.item_id not in batch_dict:
            batch_dict[b.item_id] = {"batches": [], "total_qty": 0, "has_real_expiry": False}

        batch_dict[b.item_id]["batches"].append({
            "expiration_date": b.expiration_date,
            "quantity": b.quantity
        })

        batch_dict[b.item_id]["total_qty"] += b.quantity

        # Mark if the batch has a real expiry date
        if str(b.expiration_date)[:10] != "9999-12-31":
            batch_dict[b.item_id]["has_real_expiry"] = True

    # Combine item + list of its batches and total quantity
    formatted_items = []
    for row in items:
        formatted_items.append({
            "item": {
                "item_id": row.item_id,
                "name": row.name,
                "reorder_level": row.reorder_level,
                "category_name": row.category_name
            },
            "batches": batch_dict.get(row.item_id, {}).get("batches", []),
            "total_qty": batch_dict.get(row.item_id, {}).get("total_qty", 0),
            "has_real_expiry": batch_dict.get(row.item_id, {}).get("has_real_expiry", False)
        })

    return formatted_items


def update_inventory_item(item_id, new_quantity, performed_by, expiration_date=None):
    """
    Calls the 'update_inventory' PostgreSQL function to add or replace
    a batch. If expiration_date is None or '9999-12-31', it merges into
    the single "no expiry" row. Otherwise it merges into that date row.
    """
    try:
        # First, update the inventory
        query = text("""
            SELECT update_inventory(
                :item_id,
                :new_quantity,
                :performed_by,
                :expiration_date
            ) AS result;
        """)

        result = db.session.execute(query, {
            "item_id": item_id,
            "new_quantity": new_quantity,
            "performed_by": performed_by,
            "expiration_date": expiration_date or None
        }).fetchone()

        # Fetch the current inventory levels AFTER update
        inventory_check = text("""
            SELECT i.name, i.reorder_level, SUM(b.quantity) AS total_qty
            FROM InventoryItems i
            JOIN InventoryBatches b ON i.item_id = b.item_id
            WHERE i.item_id = :item_id
            GROUP BY i.name, i.reorder_level;
        """)

        current_item = db.session.execute(inventory_check, {"item_id": item_id}).fetchone()

        db.session.commit()

        # If stock is low, create a low stock task
        if current_item and current_item.total_qty <= current_item.reorder_level:
            _create_low_stock_task_for_techs(
                item_name=current_item.name,
                item_id=item_id,
                reorder_level=current_item.reorder_level,
                current_qty=current_item.total_qty
            )
            db.session.commit()  # Ensure the task is added to the database

        if result and result.result == 'Inventory updated successfully':
            return {"message": "Inventory updated successfully"}, 200
        else:
            return {"error": "Inventory update failed"}, 400

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def create_inventory_item(item_data):
    try:
        # Ensure initial quantity is provided and is an integer.
        initial_quantity = int(item_data.get('initial_quantity', 0))
        if initial_quantity < 0:
            return {"error": "Initial quantity cannot be negative"}, 400

        # Ensure supplier name is provided.
        if not item_data.get('supplier_name'):
            return {"error": "Supplier name is required."}, 400

        # Process the expiration date:
        # Many HTML date inputs return an empty string if nothing is selected.
        expiration_date = item_data.get('expiration_date')
        if expiration_date is not None and expiration_date.strip() == "":
            expiration_date = None

        # Build the query.
        # Note that the placeholders match exactly the parameter names in the SQL function.
        query = text("""
            SELECT create_inventory_item(
                :p_item_name,
                :p_category_id,
                :p_reorder_level,
                :p_supplier_name,
                :p_contact_info,
                :p_no_expiry,
                :p_expiration_date,
                :p_initial_quantity
            ) AS result;
        """)

        # Execute the query using the matching parameter names.
        result = db.session.execute(query, {
            "p_item_name": item_data['item_name'],
            "p_category_id": item_data['category_id'],
            "p_reorder_level": item_data['reorder_level'],
            "p_supplier_name": item_data.get('supplier_name'),
            "p_contact_info": item_data.get('contact_info'),
            # Expecting the checkbox to provide "on" when checked.
            "p_no_expiry": item_data.get('no_expiry') == 'on',
            "p_expiration_date": expiration_date,
            "p_initial_quantity": initial_quantity
        }).fetchone()

        db.session.commit()

        # Check the result returned by the SQL function.
        if result and result.result == 'Item added successfully':
            return {"message": result.result}, 200
        else:
            return {"error": "Failed to add item"}, 400

    except Exception as e:
        db.session.rollback()
        return {"error": f"Database error: {str(e)}"}, 500
