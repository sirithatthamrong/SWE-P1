from sqlalchemy import text
from app import db


def get_pending_verifications():
    """
    Fetch users who have requested a role upgrade but are pending verification.
    """
    query = text("""
        SELECT user_id, username, email, requested_role
        FROM Users
        WHERE role = 'user' AND requested_role IS NOT NULL
    """)
    result = db.session.execute(query).fetchall()

    return [{"user_id": row.user_id, "username": row.username, "email": row.email, "requested_role": row.requested_role}
            for row in result]


def approve_verification(user_id):
    """
    Approve the user's requested role change.
    """
    try:
        query = text("""
            UPDATE Users
            SET role = requested_role, requested_role = NULL
            WHERE user_id = :user_id
        """)
        db.session.execute(query, {"user_id": user_id})
        db.session.commit()
        return {"message": "User verification approved!"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def reject_verification(user_id):
    """
    Reject the user's role change request.
    """
    try:
        query = text("""
            UPDATE Users
            SET requested_role = NULL
            WHERE user_id = :user_id
        """)
        db.session.execute(query, {"user_id": user_id})
        db.session.commit()
        return {"message": "User verification rejected!"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500