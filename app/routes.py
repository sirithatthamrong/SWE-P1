from crypt import methods

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


@main.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        # Fetch filters (default to None if empty)
        lab_zone_id = request.form.get('lab_zone', None)
        experiment_id = request.form.get('experiment_type', None)
        date = request.form.get('date', None)
        start_time = request.form.get('start_time', None)
        end_time = request.form.get('end_time', None)

        # Build dynamic query for filtering
        query = """
            SELECT DISTINCT lr.lab_room_id, lr.name 
            FROM LabRooms lr
            LEFT JOIN RoomEquipment re ON lr.lab_room_id = re.lab_room_id
            LEFT JOIN ExperimentEquipment ee ON re.equipment_id = ee.equipment_id
            WHERE 1=1
        """
        params = {}

        if lab_zone_id:
            query += " AND lr.lab_zone_id = :lab_zone_id"
            params["lab_zone_id"] = lab_zone_id

        if experiment_id:
            query += " AND ee.experiment_id = :experiment_id"
            params["experiment_id"] = experiment_id

        if date and start_time and end_time:
            query += """
                AND lr.lab_room_id NOT IN (
                    SELECT lab_room_id FROM RoomReservations
                    WHERE date = :date
                    AND (start_time < :end_time AND end_time > :start_time)
                )
            """
            params["date"] = date
            params["start_time"] = start_time
            params["end_time"] = end_time

        available_rooms = db.session.execute(text(query), params).fetchall()

        return jsonify({"available_rooms": [{"lab_room_id": row.lab_room_id, "name": row.name} for row in available_rooms]})

    # Fetch existing Lab Zones & Experiment Types
    lab_zones = db.session.execute(text("SELECT lab_zone_id, name FROM LabZones")).fetchall()
    experiment_types = db.session.execute(text("SELECT experiment_id, name FROM ExperimentTypes")).fetchall()

    # Fetch all available rooms initially
    all_rooms_query = text("SELECT lab_room_id, name FROM LabRooms")
    all_rooms = db.session.execute(all_rooms_query).fetchall()

    return render_template('booking.html', lab_zones=lab_zones, experiment_types=experiment_types, all_rooms=all_rooms)
