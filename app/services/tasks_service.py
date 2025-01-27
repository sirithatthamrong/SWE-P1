from datetime import datetime
from sqlalchemy import text
from app import db
from flask import jsonify


def get_tasks_for_user(user_id):
    """
    Fetch tasks assigned to a specific user.
    Prioritize overdue tasks first, then sort by due date.
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
            tt.task_name AS task_type
        FROM Tasks t
        JOIN TaskTypes tt ON t.task_type_id = tt.task_type_id
        JOIN TaskAssignments ta ON ta.task_id = t.task_id
        WHERE ta.user_id = :user_id
        ORDER BY 
            CASE 
                WHEN t.status = 'overdue' THEN 1  -- Show overdue tasks first
                ELSE 2 
            END,
            t.due_date ASC  -- Then sort by due date
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


def create_task(data, creator_id):
    """
    Create 1 row in Tasks, then multiple rows in TaskAssignments if user typed "1;2;3".
    """
    try:
        # Validate basic fields
        required = ["task_name", "task_description", "due_date", "task_type_id", "assigned_to"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

        # Validate due date
        due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
        if due_date.date() < datetime.now().date():  # Ensure date comparison ignores time
            return jsonify({"error": "Due date cannot be in the past."}), 400

        # Insert into Tasks first
        insert_task = text("""
            INSERT INTO Tasks (
                task_name,
                task_description,
                due_date,
                task_type_id,
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
                :priority,
                :creator_id,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            RETURNING task_id
        """)

        result = db.session.execute(insert_task, {
            "task_name": data["task_name"],
            "task_description": data["task_description"],
            "due_date": data["due_date"],
            "task_type_id": data["task_type_id"],
            "priority": data.get("priority", "medium"),
            "creator_id": creator_id
        })

        new_task_id = result.fetchone()[0]  # Get the newly inserted task_id

        # Parse "assigned_to" for multiple user IDs (e.g., "1;2;3")
        assigned_str = data["assigned_to"]
        user_ids = [uid.strip() for uid in assigned_str.split(';') if uid.strip()]

        # Insert into TaskAssignments for each user
        insert_assignment = text("""
            INSERT INTO TaskAssignments (task_id, user_id)
            VALUES (:task_id, :user_id)
        """)

        for uid in user_ids:
            db.session.execute(insert_assignment, {
                "task_id": new_task_id,
                "user_id": uid
            })

        db.session.commit()

        return jsonify({"message": "Task created successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def accept_task(task_id, user_id):
    try:
        query = text("SELECT accept_task(:task_id, :user_id)")
        result = db.session.execute(query, {"task_id": task_id, "user_id": user_id}).scalar()
        db.session.commit()

        if result:
            return jsonify({"message": "Task accepted."}), 200
        else:
            return jsonify({"error": "Task is not pending or not assigned to you."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def complete_task(task_id, user_id):
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
            return jsonify({"message": "Task completed!"}), 200
        else:
            return jsonify({"error": "Task is not overdue or in progress."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
