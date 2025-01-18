from sqlalchemy import text
from app import db


def get_lab_zones():
    return db.session.execute(text("SELECT lab_zone_id, name FROM LabZones")).fetchall()


def get_experiment_types():
    return db.session.execute(text("SELECT experiment_id, name FROM ExperimentTypes")).fetchall()


def get_all_rooms():
    return db.session.execute(text("SELECT lab_room_id, name FROM LabRooms")).fetchall()


def fetch_available_rooms(lab_zone_id=None, experiment_id=None, date=None, start_time=None, end_time=None):
    query = text("SELECT * FROM get_available_rooms(:p_lab_zone_id, :p_experiment_id, :p_date, :p_start_time, :p_end_time)")
    params = {
        "p_lab_zone_id": lab_zone_id if lab_zone_id else None,
        "p_experiment_id": experiment_id if experiment_id else None,
        "p_date": date if date else None,
        "p_start_time": start_time if start_time else None,
        "p_end_time": end_time if end_time else None
    }
    return db.session.execute(query, params).fetchall()
