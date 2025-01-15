from flask import (Blueprint,
                   jsonify,
                   render_template,
                   Response,
                   request,
                   flash,
                   redirect,
                   url_for,
                   session)
from sqlalchemy import text
from functools import wraps
from app import db


main = Blueprint('main', __name__)


@main.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "success", "message": "Database connected successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


@main.route('/')
@login_required
def home():
    return jsonify({"message": "Welcome to the Flask App!"})


@main.route('/login', methods=['GET', 'POST'])
def login():
    # if 'user_id' in session: return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = text(
            "SELECT user_id, password FROM Users WHERE username = :username"
        )
        result = db.session.execute(query, {'username': username}).fetchone()

        if result:
            user_id, stored_password = result

            if password == stored_password:
                session['user_id'] = user_id
                flash("Login successful!", "success")
                return redirect(url_for('main.home'))
            else:
                flash("Invalid credentials.", "danger")
        else:
            flash("User not found.", "danger")

    return render_template('login.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        query = text("SELECT username FROM Users WHERE username = :username")
        result = db.session.execute(query, {'username': username}).fetchone()

        if result:
            flash("Username already taken. Please choose another one.", "danger")
            return redirect(url_for('main.signup'))

        try:
            query = text(
                "INSERT INTO Users (username, email, password) VALUES (:username, :email, :password)"
            )
            db.session.execute(query, {'username': username, 'email': email, 'password': password})
            db.session.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('main.login'))
        except Exception as e:
            flash(f"Signup failed: {str(e)}", "danger")
            return redirect(url_for('main.signup'))

    return render_template('signup.html')


@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))

