from datetime import datetime
from sqlalchemy import text
from app import db


def get_tasks_for_user(user_id):
    query = text("SELECT * FROM get_tasks_for_user(:user_id)")
    result = db.session.execute(query, {"user_id": user_id}).fetchall()

    return [{
        "task_id": row.task_id,
        "task_name": row.task_name,
        "task_description": row.task_description,
        "due_date": row.due_date.strftime("%Y-%m-%d"),
        "priority": row.priority,
        "status": row.status,
        "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": row.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": row.created_by,
        "creator_name": row.creator_name,
        "task_type": row.task_type
    } for row in result]


def get_tasks_created_by_user(user_id):
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
            tt.task_name AS task_type
        FROM Tasks t
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
            "task_type": row.task_type
        })
    return tasks


def validate_task_data(data):
    required_fields = ["task_name", "task_description", "due_date", "task_type_id", "assigned_to"]

    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return {"error": f"Missing required field(s): {', '.join(missing)}"}, 400

    try:
        due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

    if due_date < datetime.now().date():
        return {"error": "Due date cannot be in the past."}, 400

    return None


def insert_task(data, creator_id):
    query = text("""
        INSERT INTO Tasks (
            task_name, task_description, due_date, task_type_id, priority,
            created_by, created_at, updated_at
        )
        VALUES (
            :task_name, :task_description, :due_date, :task_type_id, 
            :priority, :creator_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
        RETURNING task_id
    """)

    result = db.session.execute(query, {
        "task_name": data["task_name"],
        "task_description": data["task_description"],
        "due_date": data["due_date"],
        "task_type_id": data["task_type_id"],
        "priority": data.get("priority", "medium"),
        "creator_id": creator_id
    })

    return result.fetchone()[0]


def assign_users_to_task(task_id, assigned_users):
    try:
        user_ids = [uid.strip() for uid in assigned_users.split(';') if uid.strip()]

        if not user_ids:
            return {"error": "At least one user must be assigned."}, 400

        # Validate that all user IDs exist in the database
        valid_users_query = text("SELECT user_id FROM Users WHERE user_id IN :user_ids")
        valid_users = db.session.execute(valid_users_query, {"user_ids": tuple(user_ids)}).fetchall()
        valid_user_ids = {row.user_id for row in valid_users}

        for uid in user_ids:
            if int(uid) not in valid_user_ids:
                return {"error": f"User ID {uid} does not exist."}, 400

        insert_assignment = text("""
            INSERT INTO TaskAssignments (task_id, user_id) VALUES (:task_id, :user_id)
        """)

        for uid in user_ids:
            db.session.execute(insert_assignment, {"task_id": task_id, "user_id": uid})

    except Exception as e:
        return {"error": f"Error assigning users: {str(e)}"}, 500

    return None


def create_task(data, creator_id):
    try:
        validation_error = validate_task_data(data)
        if validation_error:
            return validation_error

        new_task_id = insert_task(data, creator_id)

        assignment_error = assign_users_to_task(new_task_id, data["assigned_to"])
        if assignment_error:
            return assignment_error

        db.session.commit()
        return {"message": "Task created successfully!"}, 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Unexpected error: {str(e)}"}, 500


def accept_task(task_id, user_id):
    try:
        query = text("SELECT accept_task(:task_id, :user_id)")
        result = db.session.execute(query, {"task_id": task_id, "user_id": user_id}).scalar()
        db.session.commit()

        if result:
            return {"message": "Task accepted."}, 200
        else:
            return {"error": "Task is not pending or not assigned to you."}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def complete_task(task_id):
    try:
        query = text("""
            UPDATE Tasks
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE task_id = :task_id
              AND status IN ('overdue', 'in progress')
            RETURNING task_id
        """)
        result = db.session.execute(query, {"task_id": task_id})
        db.session.commit()

        if result.rowcount > 0:
            return {"message": "Task completed!"}, 200
        else:
            return {"error": "Task is not overdue or in progress."}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
