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
from app import db
from datetime import datetime
from app.services.auth_service import signup_user, login_user, login_required
from app.services.tasks_service import (
    get_tasks_for_user,
    get_tasks_created_by_user,
    create_task,
    accept_task,
    complete_task
)
from app.services.booking_service import (
    get_lab_zones,
    get_experiment_types,
    get_all_rooms,
    get_available_rooms,
    get_room_details,
    get_available_time_slots,
    create_room_booking,
    has_overlapping_booking,
    is_room_already_booked,
    cancel_room_booking,
    get_upcoming_bookings
)
from app.services.calendar_service import fetch_calendar_data

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


# -------------------------------------------------------------------
#                      Booking Page
# -------------------------------------------------------------------
@main.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    today = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        lab_zone_id = request.form.get('lab_zone')
        experiment_id = request.form.get('experiment_type')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        available_rooms = get_available_rooms(lab_zone_id, experiment_id, date, start_time, end_time)

        return jsonify(
            {"available_rooms": [{"lab_room_id": row.lab_room_id, "name": row.name} for row in available_rooms]}
        )

    upcoming_bookings = get_upcoming_bookings(session.get('user_id'))

    return render_template(
        'booking.html',
        lab_zones=get_lab_zones(),
        experiment_types=get_experiment_types(),
        all_rooms=get_all_rooms(),
        future_bookings=upcoming_bookings,
        today=today
    )


@main.route('/booking/cancel/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_booking(reservation_id):
    user_id = session.get('user_id')
    success = cancel_room_booking(reservation_id, user_id)
    if success:
        return jsonify({"success": "Booking canceled successfully!"})
    else:
        return jsonify({"error": "Failed to cancel booking or unauthorized action."}), 400


@main.route('/booking/room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    date = request.args.get('date', None)

    if date:
        today = datetime.now().date()
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        if selected_date < today:
            return jsonify({"error": "You cannot book a past date."}), 400

    if request.method == 'POST':
        selected_slots = request.form.getlist('time_slot')
        user_id = session.get('user_id')
        experiment_id = request.form.get('experiment_type')

        if not selected_slots:
            return jsonify({"error": "Please select at least one time slot."}), 400

        if is_room_already_booked(room_id, date, selected_slots):
            return jsonify({"error": "One or more selected slots are already booked."}), 400

        if has_overlapping_booking(user_id, date, selected_slots):
            return jsonify({"error": "You already have a conflicting booking for this time slot in another room."}), 400

        reservation_id = create_room_booking(user_id, room_id, experiment_id, date, selected_slots)
        if reservation_id:
            return jsonify({"success": "Booking confirmed!"})
        else:
            return jsonify({"error": "Booking failed, try again."}), 500

    room_details = get_room_details(room_id)
    available_slots = get_available_time_slots(room_id, date)

    return render_template(
        'room_booking.html',
        room_details=room_details,
        available_slots=available_slots,
        lab_zones=get_lab_zones(),
        experiment_types=get_experiment_types(),
        selected_date=date
    )


# -------------------------------------------------------------------
#                      My Calendar Page
# -------------------------------------------------------------------
@main.route('/calendar', methods=['GET'])
@login_required
def calendar():
    user_id = session.get('user_id')

    calendar_data = fetch_calendar_data(user_id)

    return render_template(
        'calendar.html',
        reservations=calendar_data["reservations"],
        upcoming_reservations=calendar_data["upcoming_reservations"],
        tasks=calendar_data["tasks"],
        task_counts=calendar_data["task_counts"],
    )