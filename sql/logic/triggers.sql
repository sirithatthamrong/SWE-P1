DROP TRIGGER IF EXISTS check_booking_overlap ON RoomReservations;
CREATE TRIGGER check_booking_overlap
    BEFORE INSERT
    ON RoomReservations
    FOR EACH ROW
EXECUTE FUNCTION prevent_double_booking();

DROP TRIGGER IF EXISTS auto_archive_old_reservations ON RoomReservations;
CREATE TRIGGER auto_archive_old_reservations
    BEFORE INSERT OR UPDATE
    ON RoomReservations
    FOR EACH ROW
EXECUTE FUNCTION archive_old_reservations();

DROP TRIGGER IF EXISTS trigger_update_overdue_tasks ON Tasks;
CREATE TRIGGER trigger_update_overdue_tasks
    BEFORE INSERT OR UPDATE
    ON Tasks
    FOR EACH ROW
EXECUTE FUNCTION update_overdue_tasks();
