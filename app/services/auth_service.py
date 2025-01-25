from sqlalchemy import text
from flask import (flash,
                   redirect,
                   url_for,
                   session)
from functools import wraps
from app import db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


def signup_user(username, email, password, role):
    query = text("SELECT username FROM Users WHERE username = :username")
    result = db.session.execute(query, {'username': username}).fetchone()

    if result:
        flash("Username already taken. Please choose another one.", "danger")
        return False

    try:
        query = text(
            "INSERT INTO Users (username, email, password, role) VALUES (:username, :email, :password, :role)"
        )
        db.session.execute(query, {'username': username, 'email': email, 'password': password, 'role': role})
        db.session.commit()
        flash("Signup successful! Please log in.", "success")
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"Signup failed: {str(e)}", "danger")
        return False


def login_user(username, password):
    query = text(
        "SELECT user_id, password FROM Users WHERE username = :username"
    )
    result = db.session.execute(query, {'username': username}).fetchone()

    if result:
        user_id, stored_password = result

        if password == stored_password:
            session['user_id'] = user_id
            flash("Login successful!", "success")
            return True
        else:
            flash("Invalid credentials.", "danger")
    else:
        flash("User not found.", "danger")

    return False