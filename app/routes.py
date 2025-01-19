from flask import (Blueprint,
                   jsonify,
                   render_template,
                   request,
                   flash,
                   redirect,
                   url_for,
                   session)
from sqlalchemy import text
from app import db
from app.services.auth_service import signup_user, login_user, login_required
from app.services.booking_service import get_lab_zones, get_experiment_types, get_all_rooms, get_available_rooms, \
    get_room_details, get_available_time_slots, create_room_booking, has_overlapping_booking, is_room_already_booked

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


@main.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        lab_zone_id = request.form.get('lab_zone')
        experiment_id = request.form.get('experiment_type')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        available_rooms = get_available_rooms(lab_zone_id, experiment_id, date, start_time, end_time)

        return jsonify(
            {"available_rooms": [{"lab_room_id": row.lab_room_id, "name": row.name} for row in available_rooms]})

    return render_template(
        'booking.html',
        lab_zones=get_lab_zones(),
        experiment_types=get_experiment_types(),
        all_rooms=get_all_rooms()
    )


@main.route('/booking/room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    date = request.args.get('date', None)

    if request.method == 'POST':
        selected_slots = request.form.getlist('time_slot')
        user_id = session.get('user_id')
        experiment_id = request.form.get('experiment_type')

        # Ensure at least one time slot is selected
        if not selected_slots:
            return jsonify({"error": "Please select at least one time slot."}), 400

        # Ensure user is not booking another room at the same time
        if has_overlapping_booking(user_id, date, selected_slots):
            return jsonify({"error": "You already have a conflicting booking for this time slot in another room."}), 400

        # Ensure this room isn't already booked for the selected slots
        if is_room_already_booked(room_id, date, selected_slots):
            return jsonify({"error": "One or more selected slots are already booked."}), 400

        # Insert Booking
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



