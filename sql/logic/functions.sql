CREATE OR REPLACE FUNCTION prevent_double_booking()
    RETURNS TRIGGER AS
$$
BEGIN
    -- Check if the room is already booked
    IF EXISTS (SELECT 1
               FROM RoomReservations
               WHERE lab_room_id = NEW.lab_room_id
                 AND date = NEW.date
                 AND (NEW.start_time < end_time AND NEW.end_time > start_time)) THEN
        RAISE EXCEPTION 'Room is already booked for the selected time!';
    END IF;

    -- Check if the user has overlapping booking
    IF EXISTS (SELECT 1
               FROM RoomReservations
               WHERE user_id = NEW.user_id
                 AND date = NEW.date
                 AND (NEW.start_time < end_time AND NEW.end_time > start_time)) THEN
        RAISE EXCEPTION 'You already have a booking that overlaps with this time slot!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- This function enforces that no null/empty fields are inserted
-- and that the due_date is >= current_date.
CREATE OR REPLACE FUNCTION tasks_validation()
    RETURNS TRIGGER AS
$$
BEGIN
    -- Check due_date is in the future (or today)
    IF NEW.due_date < CURRENT_DATE THEN
        RAISE EXCEPTION 'Due date cannot be in the past.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION accept_task(p_task_id INTEGER, p_user_id INTEGER)
    RETURNS BOOLEAN AS
$$
BEGIN
    UPDATE Tasks
    SET status     = 'in progress',
        updated_at = CURRENT_TIMESTAMP
    WHERE task_id = p_task_id
      AND status = 'pending'
      AND EXISTS (SELECT 1
                  FROM TaskAssignments
                  WHERE task_id = p_task_id
                    AND user_id = p_user_id);

    IF FOUND THEN
        RETURN TRUE; -- Task updated
    ELSE
        RETURN FALSE; -- Not updated
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION complete_task(p_task_id INTEGER, p_user_id INTEGER)
    RETURNS BOOLEAN AS
$$
BEGIN
    UPDATE Tasks
    SET status       = 'completed',
        completed_at = CURRENT_TIMESTAMP,
        updated_at   = CURRENT_TIMESTAMP
    WHERE task_id = p_task_id
      AND assigned_to = p_user_id
      AND status = 'in progress';

    IF FOUND THEN
        RETURN TRUE; -- Task successfully updated
    ELSE
        RETURN FALSE; -- Task not updated (e.g., wrong status or user)
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_available_rooms(
    p_lab_zone_id INT DEFAULT NULL,
    p_experiment_id INT DEFAULT NULL,
    p_date DATE DEFAULT NULL,
    p_start_time TIME DEFAULT NULL,
    p_end_time TIME DEFAULT NULL
)
    RETURNS TABLE
            (
                lab_room_id INT,
                name        VARCHAR
            )
AS
$$
BEGIN
    RETURN QUERY
        SELECT DISTINCT lr.lab_room_id, lr.name
        FROM LabRooms lr
                 LEFT JOIN RoomEquipment re ON lr.lab_room_id = re.lab_room_id
                 LEFT JOIN ExperimentEquipment ee ON re.equipment_id = ee.equipment_id
        WHERE (p_lab_zone_id IS NULL OR lr.lab_zone_id = p_lab_zone_id)
          AND (p_experiment_id IS NULL OR ee.experiment_id = p_experiment_id)
          AND (p_date IS NULL OR NOT EXISTS (SELECT 1
                                             FROM RoomReservations r
                                             WHERE r.lab_room_id = lr.lab_room_id
                                               AND r.date = p_date
                                               AND (r.start_time < p_end_time AND r.end_time > p_start_time)));
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION archive_old_reservations()
    RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.date < CURRENT_DATE THEN
        UPDATE RoomReservations
        SET action = 'archived'
        WHERE reservation_id = NEW.reservation_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;