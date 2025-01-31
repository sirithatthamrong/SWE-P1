from functools import wraps

from flask import flash, redirect, session, url_for
from sqlalchemy import text

from app import db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            user_role = session.get("user_role")
            print(f"DEBUG: User role in session: {user_role}")  # Debug log
            if user_role not in roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(
                    url_for("main.home")
                )  # Redirect to home page or another safe page
            return f(*args, **kwargs)

        return wrapped_function

    return decorator


def signup_user(username, email, password, role):
    query = text("SELECT username FROM Users WHERE username = :username")
    result = db.session.execute(query, {"username": username}).fetchone()

    if result:
        flash("Username already taken. Please choose another one.", "danger")
        return False

    try:
        # If the role is not 'user', request verification
        requested_role = role if role != "user" else None
        actual_role = "user"  # Default role

        query = text(
            """
            INSERT INTO Users (username, email, password, role, requested_role)
            VALUES (:username, :email, :password, :role, :requested_role)
        """
        )
        db.session.execute(
            query,
            {
                "username": username,
                "email": email,
                "password": password,
                "role": actual_role,
                "requested_role": requested_role,
            },
        )
        db.session.commit()

        flash(
            "Signup successful! If you requested a role, an admin will verify it.",
            "success",
        )
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"Signup failed: {str(e)}", "danger")
        return False


def login_user(username, password):
    query = text("SELECT user_id, password, role FROM Users WHERE username = :username")
    result = db.session.execute(query, {"username": username}).fetchone()

    if result:
        user_id, stored_password, user_role = result

        if password == stored_password:
            session["user_id"] = user_id
            session["user_role"] = user_role
            flash("Login successful!", "success")
            return True
        else:
            flash("Invalid credentials.", "danger")
    else:
        flash("User not found.", "danger")

    return False
