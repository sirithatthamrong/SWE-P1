CREATE OR REPLACE FUNCTION validate_room_reservation()
    RETURNS TRIGGER AS
$$
BEGIN
    IF EXISTS (SELECT 1
               FROM RoomReservations
               WHERE user_id = NEW.user_id
                 AND (
                   (start_time < NEW.end_time AND end_time > NEW.start_time)
                   )) THEN
        RAISE EXCEPTION 'User already has a reservation during this time.';
    END IF;

    IF EXISTS (SELECT 1
               FROM RoomReservations
               WHERE lab_room_id = NEW.lab_room_id
                 AND (
                   (start_time < NEW.end_time AND end_time > NEW.start_time)
                   )) THEN
        RAISE EXCEPTION 'Lab room is already reserved during this time.';
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
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE Tasks
    SET status = 'in progress',
        updated_at = CURRENT_TIMESTAMP
    WHERE task_id = p_task_id
      AND status = 'pending'
      AND EXISTS (
          SELECT 1 FROM TaskAssignments
          WHERE task_id = p_task_id
            AND user_id = p_user_id
      );

    IF FOUND THEN
        RETURN TRUE; -- Task updated
    ELSE
        RETURN FALSE; -- Not updated
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION complete_task(p_task_id INTEGER, p_user_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE Tasks
    SET status = 'completed',
        completed_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
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