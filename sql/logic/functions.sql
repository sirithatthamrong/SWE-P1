CREATE OR REPLACE FUNCTION prevent_double_booking()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the room is already booked
    IF EXISTS (
        SELECT 1 FROM RoomReservations
        WHERE lab_room_id = NEW.lab_room_id
        AND date = NEW.date
        AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        RAISE EXCEPTION 'Room is already booked for the selected time!';
    END IF;

    -- Check if the user has overlapping booking
    IF EXISTS (
        SELECT 1 FROM RoomReservations
        WHERE user_id = NEW.user_id
        AND date = NEW.date
        AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        RAISE EXCEPTION 'You already have a booking that overlaps with this time slot!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;