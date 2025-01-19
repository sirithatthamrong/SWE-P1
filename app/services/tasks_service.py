# app/services/tasks_service.py

from datetime import datetime
from sqlalchemy import text
from app import db

def get_tasks_for_user(user_id):
    """
    Fetch tasks *assigned* to a specific user.
    """
    query = text("""
        SELECT
            t.task_id,
            t.task_name,
            t.task_description,
            t.due_date,
            t.priority,
            t.status,
            t.created_at,
            t.updated_at,
            t.created_by,
            u.username AS assigned_by,
            tt.task_name AS task_type
        FROM Tasks t
        JOIN Users u ON t.assigned_to = u.user_id
        JOIN TaskTypes tt ON t.task_type_id = tt.task_type_id
        WHERE t.assigned_to = :user_id
        ORDER BY t.due_date ASC
    """)

    result = db.session.execute(query, {"user_id": user_id}).fetchall()

    tasks = []
    for row in result:
        tasks.append({
            "task_id": row.task_id,
            "task_name": row.task_name,
            "task_description": row.task_description,
            "due_date": row.due_date.strftime("%Y-%m-%d"),
            "priority": row.priority,
            "status": row.status,
            "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": row.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": row.created_by,
            "assigned_by": row.assigned_by,
            "task_type": row.task_type
        })
    return tasks

def get_tasks_created_by_user(user_id):
    """
    Fetch tasks CREATED by a specific user (i.e. tasks.created_by = user_id).
    """
    query = text("""
        SELECT
            t.task_id,
            t.task_name,
            t.task_description,
            t.due_date,
            t.priority,
            t.status,
            t.created_at,
            t.updated_at,
            t.created_by,
            u.username AS assigned_user,
            tt.task_name AS task_type
        FROM Tasks t
        JOIN Users u ON t.assigned_to = u.user_id
        JOIN TaskTypes tt ON t.task_type_id = tt.task_type_id
        WHERE t.created_by = :user_id
        ORDER BY t.created_at DESC
    """)
    result = db.session.execute(query, {"user_id": user_id}).fetchall()

    tasks = []
    for row in result:
        tasks.append({
            "task_id": row.task_id,
            "task_name": row.task_name,
            "task_description": row.task_description,
            "due_date": row.due_date.strftime("%Y-%m-%d"),
            "priority": row.priority,
            "status": row.status,
            "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": row.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": row.created_by,
            "assigned_user": row.assigned_user,
            "task_type": row.task_type
        })
    return tasks

def create_task(data, creator_id):
    """
    Create a new task. 'creator_id' = the user who created the task.
    The DB trigger 'tasks_validation' enforces certain constraints.
    """
    try:
        required = ["task_name", "task_description", "due_date", "task_type_id", "assigned_to"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return {"error": f"Missing required field(s): {', '.join(missing)}"}, 400

        query = text("""
            INSERT INTO Tasks (
                task_name,
                task_description,
                due_date,
                task_type_id,
                assigned_to,
                priority,
                created_by,
                created_at,
                updated_at
            )
            VALUES (
                :task_name,
                :task_description,
                :due_date,
                :task_type_id,
                :assigned_to,
                :priority,
                :created_by,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
        """)

        db.session.execute(query, {
            "task_name": data.get("task_name"),
            "task_description": data.get("task_description"),
            "due_date": data.get("due_date"),
            "task_type_id": data.get("task_type_id"),
            "assigned_to": data.get("assigned_to"),
            "priority": data.get("priority", "medium"),
            "created_by": creator_id
        })
        db.session.commit()

        return {"message": "Task created successfully!"}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def accept_task(task_id, user_id):
    """
    Call the 'accept_task' SQL function to update the task status.
    """
    try:
        query = text("SELECT accept_task(:task_id, :user_id)")
        result = db.session.execute(query, {"task_id": task_id, "user_id": user_id}).scalar()
        db.session.commit()

        if result:  # Check if the task was successfully accepted
            return {"message": "Task accepted."}, 200
        else:
            return {"error": "Task is not pending or not assigned to you."}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def complete_task(task_id, user_id):
    """
    Call the 'complete_task' SQL function to update the task status.
    """
    try:
        query = text("SELECT complete_task(:task_id, :user_id)")
        result = db.session.execute(query, {"task_id": task_id, "user_id": user_id}).scalar()
        db.session.commit()

        if result:  # Check if the task was successfully completed
            return {"message": "Task completed!"}, 200
        else:
            return {"error": "Task is not in progress or not assigned to you."}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500