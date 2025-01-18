from crypt import methods

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
from app.services.booking_service import get_lab_zones, get_experiment_types, get_all_rooms, fetch_available_rooms

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

        available_rooms = fetch_available_rooms(lab_zone_id, experiment_id, date, start_time, end_time)

        return jsonify({"available_rooms": [{"lab_room_id": row.lab_room_id, "name": row.name} for row in available_rooms]})

    return render_template(
        'booking.html',
        lab_zones=get_lab_zones(),
        experiment_types=get_experiment_types(),
        all_rooms=get_all_rooms()
    )