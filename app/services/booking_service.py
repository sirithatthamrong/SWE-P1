from sqlalchemy import text
from app import db
from datetime import datetime, timedelta


def get_lab_zones():
    return db.session.execute(text("SELECT lab_zone_id, name FROM LabZones")).fetchall()


def get_experiment_types():
    return db.session.execute(text("SELECT experiment_id, name FROM ExperimentTypes")).fetchall()


def get_all_rooms():
    return db.session.execute(text("SELECT lab_room_id, name FROM LabRooms")).fetchall()


def get_available_rooms(lab_zone_id=None, experiment_id=None, date=None, start_time=None, end_time=None):
    query = text(
        "SELECT * FROM get_available_rooms(:p_lab_zone_id, :p_experiment_id, :p_date, :p_start_time, :p_end_time)")
    params = {
        "p_lab_zone_id": lab_zone_id if lab_zone_id else None,
        "p_experiment_id": experiment_id if experiment_id else None,
        "p_date": date if date else None,
        "p_start_time": start_time if start_time else None,
        "p_end_time": end_time if end_time else None
    }
    return db.session.execute(query, params).fetchall()


def get_room_details(room_id):
    query = text("""
        SELECT lr.lab_room_id, lr.name, lr.location, lz.name AS lab_zone
        FROM LabRooms lr
        JOIN LabZones lz ON lr.lab_zone_id = lz.lab_zone_id
        WHERE lr.lab_room_id = :room_id
    """)
    return db.session.execute(query, {"room_id": room_id}).fetchone()


def get_available_time_slots(room_id, date):
    if not date:
        return []

    query = text("""
        WITH all_slots AS (
            SELECT (generate_series(
                '2025-01-01 08:00:00'::timestamp, 
                '2025-01-01 17:00:00'::timestamp, 
                '1 hour'::interval
            ))::time AS start_time
        )
        SELECT 
            all_slots.start_time, 
            (all_slots.start_time + INTERVAL '1 hour') AS end_time
        FROM all_slots
        LEFT JOIN RoomReservations rr
        ON rr.lab_room_id = :room_id 
        AND rr.date = :date
        AND rr.action = 'active'
        AND all_slots.start_time >= rr.start_time  -- Ensure it covers overlapping range
        AND all_slots.start_time < rr.end_time
        WHERE rr.reservation_id IS NULL  -- Exclude booked slots
        ORDER BY all_slots.start_time;
    """)

    return db.session.execute(query, {"room_id": room_id, "date": date}).fetchall()


def has_overlapping_booking(user_id, date, selected_slots):
    """Check if user has overlapping reservations, even in different rooms."""
    if not selected_slots:
        return False

    query = text("""
        SELECT 1 FROM RoomReservations
        WHERE user_id = :user_id
        AND date = :date
        AND action = 'active'
        AND (
            start_time = ANY(ARRAY[:selected_slots]::time[])
            OR EXISTS (
                SELECT 1 FROM RoomReservations
                WHERE user_id = :user_id
                AND action = 'active'
                AND date = :date
                AND start_time < ANY(ARRAY[:selected_slots]::time[])
                AND end_time > ANY(ARRAY[:selected_slots]::time[])
            )
        )
    """)

    return db.session.execute(query, {
        "user_id": user_id,
        "date": date,
        "selected_slots": list(selected_slots)
    }).fetchone()


def is_room_already_booked(room_id, date, selected_slots):
    """Check if the selected room is already booked for the selected slots."""
    if not selected_slots:
        return False

    query = text("""
        SELECT 1 FROM RoomReservations
        WHERE lab_room_id = :room_id
        AND date = :date
        AND action = 'active'
        AND start_time = ANY(ARRAY[:selected_slots]::time[])
    """)

    return db.session.execute(query, {
        "room_id": room_id,
        "date": date,
        "selected_slots": list(selected_slots)
    }).fetchone()


def create_room_booking(user_id, room_id, experiment_id, date, selected_slots):
    try:
        lab_zone_query = text("SELECT lab_zone_id FROM LabRooms WHERE lab_room_id = :room_id")
        lab_zone_id = db.session.execute(lab_zone_query, {"room_id": room_id}).scalar()

        sorted_slots = sorted([datetime.strptime(slot, "%H:%M:%S") for slot in selected_slots])

        for slot in sorted_slots:
            start_time = slot
            end_time = slot + timedelta(hours=1)

            query = text("""
                INSERT INTO RoomReservations (user_id, lab_zone_id, lab_room_id, experiment_id, date, start_time, end_time)
                VALUES (:user_id, :lab_zone_id, :room_id, :experiment_id, :date, :start_time, :end_time)
            """)
            db.session.execute(query, {
                "user_id": user_id,
                "lab_zone_id": lab_zone_id,
                "room_id": room_id,
                "experiment_id": experiment_id if experiment_id else None,
                "date": date,
                "start_time": start_time.strftime("%H:%M:%S"),
                "end_time": end_time.strftime("%H:%M:%S")
            })

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Booking Error: {e}")
        return False


def get_upcoming_bookings(user_id):
    query = text("""
        SELECT rr.reservation_id, rr.date, rr.start_time, rr.end_time, lr.name AS room_name
        FROM RoomReservations rr
        JOIN LabRooms lr ON rr.lab_room_id = lr.lab_room_id
        WHERE rr.user_id = :user_id 
            AND rr.date >= CURRENT_DATE
            AND rr.action = 'active'
        ORDER BY rr.date, rr.start_time;
    """)

    return db.session.execute(query, {"user_id": user_id}).fetchall()


def cancel_room_booking(reservation_id, user_id):
    try:
        check_query = text("""
            SELECT user_id FROM RoomReservations 
            WHERE reservation_id = :reservation_id AND action = 'active'
        """)
        result = db.session.execute(check_query, {"reservation_id": reservation_id}).fetchone()

        if result is None or result.user_id != user_id:
            return False

        update_query = text("""
            UPDATE RoomReservations
            SET action = 'canceled'
            WHERE reservation_id = :reservation_id
        """)
        db.session.execute(update_query, {"reservation_id": reservation_id})

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Cancellation Error: {e}")
        return False