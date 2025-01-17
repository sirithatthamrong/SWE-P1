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
from app.services.auth_service import signup_user, login_user, login_required


main = Blueprint('main', __name__)


@main.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "success", "message": "Database connected successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@main.route('/')
@login_required
def home():
    return render_template('home.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if login_user(username, password):
            return redirect(url_for('main.home'))

    return render_template('login.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if signup_user(username, email, password):
            return redirect(url_for('main.login'))

    return render_template('signup.html')


@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))
