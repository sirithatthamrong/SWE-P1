from sqlalchemy import text
from datetime import datetime
from app import db


def fetch_calendar_data(user_id):
    # Fetch reservations
    reservations_query = text("""
        SELECT 
            R.reservation_id, 
            R.date, 
            R.start_time,
            R.end_time,
            R.action AS status, 
            L.lab_zone_id, 
            L.name AS room_name
        FROM RoomReservations R
        JOIN LabRooms L 
            ON R.lab_room_id = L.lab_room_id
        WHERE R.user_id = :user_id  
          AND R.action IN ('active', 'archived')
        ORDER BY R.date ASC, R.start_time ASC
    """)
    reservations_result = db.session.execute(reservations_query, {"user_id": user_id})

    reservations = [
        {
            "reservation_id": res.reservation_id,
            "date": res.date.isoformat(),
            "start_time": str(res.start_time),
            "end_time": str(res.end_time),
            "status": res.status,
            "lab_zone_id": res.lab_zone_id,
            "room_name": res.room_name,
        }
        for res in reservations_result
    ]

    # Filter upcoming reservations
    upcoming_reservations = [res for res in reservations]

    # Fetch tasks assigned to the user (including the ones they created)
    tasks_query = text("""
        SELECT T.task_id, T.task_name, T.priority, T.status, T.due_date
        FROM Tasks T
        JOIN TaskAssignments TA ON T.task_id = TA.task_id
        WHERE TA.user_id = :user_id 
          AND T.status NOT IN ('completed')
        ORDER BY T.due_date
    """)
    tasks_result = db.session.execute(tasks_query, {"user_id": user_id})

    tasks = [
        {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat(),
        }
        for task in tasks_result
    ]

    # Group tasks by priority
    task_counts = {"high": 0, "medium": 0, "low": 0}
    for task in tasks:
        if task["priority"] in task_counts:
            task_counts[task["priority"]] += 1

    return {
        "reservations": reservations,
        "upcoming_reservations": upcoming_reservations,
        "tasks": tasks,
        "task_counts": task_counts
    }
