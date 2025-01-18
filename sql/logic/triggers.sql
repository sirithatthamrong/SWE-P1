DROP TRIGGER IF EXISTS check_room_reservation_overlap ON RoomReservations;
CREATE TRIGGER check_room_reservation_overlap
BEFORE INSERT OR UPDATE ON RoomReservations
FOR EACH ROW
EXECUTE FUNCTION validate_room_reservation();


DROP TRIGGER IF EXISTS tasks_validation_trigger ON Tasks;

CREATE TRIGGER tasks_validation_trigger
BEFORE INSERT OR UPDATE
ON Tasks
FOR EACH ROW
EXECUTE FUNCTION tasks_validation();