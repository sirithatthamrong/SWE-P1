# app/routes.py

from flask import (
    Blueprint,
    jsonify,
    render_template,
    Response,
    request,
    flash,
    redirect,
    url_for,
    session
)
from sqlalchemy import text
from functools import wraps
from app import db
from app.services.auth_service import signup_user, login_user, login_required
from app.services.tasks_service import get_tasks_for_user, create_task

main = Blueprint('main', __name__)


# -------------------------------------------------------------------
#                      Health Check
# -------------------------------------------------------------------
@main.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "success", "message": "Database connected successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -------------------------------------------------------------------
#                      Auth / Main Routes
# -------------------------------------------------------------------
@main.route('/')
@login_required
def home():
    # Renders your "home.html"
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


# -------------------------------------------------------------------
#                      Tasks Page (View + Create)
# -------------------------------------------------------------------
@main.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks_page():
    user_id = session.get('user_id')
    if not user_id:
        return "User not found in session", 401

    # 1. Handle POST: create a task
    if request.method == 'POST':
        data = request.form
        response, status_code = create_task(data)
        if status_code == 201:
            flash("Task created successfully!", "success")
        else:
            flash(response.get("error"), "danger")

        return redirect(url_for('main.tasks_page'))

    # 2. Handle GET: display the page with tasks + TaskTypes dropdown

    # Fetch user's tasks
    tasks = get_tasks_for_user(user_id)

    # Fetch all TaskTypes for the dropdown
    task_types_query = text("SELECT task_type_id, task_name FROM TaskTypes")
    task_types_result = db.session.execute(task_types_query).fetchall()
    task_types = [
        {"id": row.task_type_id, "name": row.task_name}
        for row in task_types_result
    ]

    # Render tasks.html, passing both tasks and task_types
    return render_template('tasks.html', tasks=tasks, task_types=task_types)
