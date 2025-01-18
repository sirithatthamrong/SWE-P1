CREATE TRIGGER check_booking_overlap
BEFORE INSERT ON RoomReservations
FOR EACH ROW
EXECUTE FUNCTION prevent_double_booking();