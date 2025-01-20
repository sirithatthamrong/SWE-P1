from flask import (
    Blueprint,
    jsonify,
    render_template,
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
from app.services.tasks_service import (
    get_tasks_for_user,
    get_tasks_created_by_user,
    create_task,
    accept_task,
    complete_task
)

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
#                   Tasks Page (View + Create)
# -------------------------------------------------------------------
@main.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks_page():
    user_id = session.get('user_id')
    if not user_id:
        return "User not found in session", 401

    if request.method == 'POST':
        data = request.form
        response, status_code = create_task(data, creator_id=user_id)
        if status_code == 201:
            flash("Task created successfully!", "success")
        else:
            flash(response.get("error"), "danger")
        return redirect(url_for('main.tasks_page'))

    # --- On GET: read which tab should be active
    active_tab = request.args.get('tab', 'my-tasks')

    # get user tasks
    tasks_assigned = get_tasks_for_user(user_id)
    my_created_tasks = get_tasks_created_by_user(user_id)

    # get TaskTypes
    task_types_query = text("SELECT task_type_id, task_name FROM TaskTypes")
    task_types_result = db.session.execute(task_types_query).fetchall()
    task_types = [
        {"id": row.task_type_id, "name": row.task_name}
        for row in task_types_result
    ]

    return render_template(
        'tasks.html',
        tasks=tasks_assigned,
        my_created_tasks=my_created_tasks,
        task_types=task_types,
        active_tab=active_tab  # pass to template
    )


@main.route('/tasks/<int:task_id>/accept', methods=['POST'])
@login_required
def accept_task_route(task_id):
    """
    Called when user accepts a pending task.
    We read ?tab=..., then redirect back to tasks_page with that tab.
    """
    user_id = session.get('user_id')
    next_tab = request.args.get('tab', 'my-tasks')  # default to 'my-tasks'

    response, status_code = accept_task(task_id, user_id)
    if status_code == 200:
        flash("Task accepted!", "success")
    else:
        flash(response.get("error"), "danger")

    return redirect(url_for('main.tasks_page', tab=next_tab))


@main.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task_route(task_id):
    """
    Called when user completes a task in progress.
    We read ?tab=..., then redirect back with that tab.
    """
    user_id = session.get('user_id')
    next_tab = request.args.get('tab', 'in-progress')  # default 'in-progress'

    response, status_code = complete_task(task_id, user_id)
    if status_code == 200:
        flash("Task completed!", "success")
    else:
        flash(response.get("error"), "danger")

    return redirect(url_for('main.tasks_page', tab=next_tab))


@main.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task_route(task_id):
    """
    Only the user who created the task can delete it.
    We'll read ?tab=..., then redirect back to that tab
    (often 'my-creations').
    """
    user_id = session.get('user_id')
    next_tab = request.args.get('tab', 'my-creations')

    try:
        query = text("""
            DELETE FROM Tasks
            WHERE task_id = :task_id
              AND created_by = :user_id
            RETURNING task_id
        """)
        result = db.session.execute(query, {
            "task_id": task_id,
            "user_id": user_id
        })
        row = result.fetchone()
        db.session.commit()

        if row:
            flash("Task deleted successfully!", "success")
        else:
            flash("You do not own this task or it does not exist.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")

    return redirect(url_for('main.tasks_page', tab=next_tab))