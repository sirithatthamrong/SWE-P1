DROP TRIGGER IF EXISTS check_booking_overlap ON RoomReservations;
CREATE TRIGGER check_booking_overlap
BEFORE INSERT ON RoomReservations
FOR EACH ROW
EXECUTE FUNCTION prevent_double_booking();


DROP TRIGGER IF EXISTS tasks_validation_trigger ON Tasks;
CREATE TRIGGER tasks_validation_trigger
BEFORE INSERT OR UPDATE
ON Tasks
FOR EACH ROW
EXECUTE FUNCTION tasks_validation();
