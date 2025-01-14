CREATE OR REPLACE FUNCTION validate_room_reservation()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM RoomReservations
        WHERE user_id = NEW.user_id
          AND (
              (start_time < NEW.end_time AND end_time > NEW.start_time)
          )
    ) THEN
        RAISE EXCEPTION 'User already has a reservation during this time.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM RoomReservations
        WHERE lab_room_id = NEW.lab_room_id
          AND (
              (start_time < NEW.end_time AND end_time > NEW.start_time)
          )
    ) THEN
        RAISE EXCEPTION 'Lab room is already reserved during this time.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

