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
    Updates an inventory item using the `update_inventory` SQL function.
    """
    try:
        query = text("""
            SELECT update_inventory(:item_id, :new_quantity, :performed_by) AS result;
        """)
        result = db.session.execute(query, {
            "item_id": item_id,
            "new_quantity": new_quantity,
            "performed_by": performed_by
        }).fetchone()

        db.session.commit()
        return {"message": result.result}, 200
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
