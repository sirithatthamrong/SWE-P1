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
    -- Check required fields
    IF NEW.task_name IS NULL
        OR NEW.task_description IS NULL
        OR NEW.due_date IS NULL
        OR NEW.task_type_id IS NULL
        OR NEW.assigned_to IS NULL THEN

        RAISE EXCEPTION 'Missing required fields: name, description, due_date, task_type_id, assigned_to cannot be null';
    END IF;

    -- Check due_date is in the future (or today)
    IF NEW.due_date < CURRENT_DATE THEN
        RAISE EXCEPTION 'Due date cannot be in the past.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;