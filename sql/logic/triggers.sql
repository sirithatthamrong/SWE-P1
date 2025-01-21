DROP TRIGGER IF EXISTS check_booking_overlap ON RoomReservations;
CREATE TRIGGER check_booking_overlap
    BEFORE INSERT
    ON RoomReservations
    FOR EACH ROW
EXECUTE FUNCTION prevent_double_booking();


DROP TRIGGER IF EXISTS tasks_validation_trigger ON Tasks;
CREATE TRIGGER tasks_validation_trigger
    BEFORE INSERT OR UPDATE
    ON Tasks
    FOR EACH ROW
EXECUTE FUNCTION tasks_validation();

DROP TRIGGER IF EXISTS auto_archive_old_reservations ON RoomReservations;
CREATE TRIGGER auto_archive_old_reservations
    AFTER INSERT OR UPDATE
    ON RoomReservations
    FOR EACH ROW
    WHEN (NEW.date < CURRENT_DATE) -- Runs only for past reservations
EXECUTE FUNCTION archive_old_reservations();