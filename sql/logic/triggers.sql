DROP TRIGGER IF EXISTS check_room_reservation_overlap ON RoomReservations;
CREATE TRIGGER check_room_reservation_overlap
BEFORE INSERT OR UPDATE ON RoomReservations
FOR EACH ROW
EXECUTE FUNCTION validate_room_reservation();
