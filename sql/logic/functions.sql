CREATE OR REPLACE FUNCTION prevent_double_booking()
    RETURNS TRIGGER AS
$$
BEGIN
    -- Check if the room is already booked
    IF EXISTS (SELECT 1
               FROM RoomReservations
               WHERE lab_room_id = NEW.lab_room_id
                 AND date = NEW.date
                 AND action = 'active'
                 AND (NEW.start_time < end_time AND NEW.end_time > start_time)) THEN
        RAISE EXCEPTION 'Room is already booked for the selected time!';
    END IF;

    -- Check if the user has overlapping booking
    IF EXISTS (SELECT 1
               FROM RoomReservations
               WHERE user_id = NEW.user_id
                 AND date = NEW.date
                 AND action = 'active'
                 AND (NEW.start_time < end_time AND NEW.end_time > start_time)) THEN
        RAISE EXCEPTION 'You already have a booking that overlaps with this time slot!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_available_rooms(
    p_lab_zone_id INT DEFAULT NULL,
    p_experiment_id INT DEFAULT NULL,
    p_date DATE DEFAULT NULL,
    p_start_time TIME DEFAULT NULL,
    p_end_time TIME DEFAULT NULL
)
    RETURNS TABLE
            (
                lab_room_id INT,
                name        VARCHAR
            )
AS
$$
BEGIN
    RETURN QUERY
        SELECT DISTINCT lr.lab_room_id, lr.name
        FROM LabRooms lr
                 LEFT JOIN RoomEquipment re ON lr.lab_room_id = re.lab_room_id
                 LEFT JOIN ExperimentEquipment ee ON re.equipment_id = ee.equipment_id
        WHERE (p_lab_zone_id IS NULL OR lr.lab_zone_id = p_lab_zone_id)
          AND (p_experiment_id IS NULL OR ee.experiment_id = p_experiment_id)
          AND (p_date IS NULL OR NOT EXISTS (SELECT 1
                                             FROM RoomReservations r
                                             WHERE r.lab_room_id = lr.lab_room_id
                                               AND r.date = p_date
                                               AND r.action = 'active'
                                               AND (r.start_time < p_end_time AND r.end_time > p_start_time)));
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION archive_old_reservations()
    RETURNS TRIGGER AS
$$
BEGIN
    -- Archive the current row if it's in the past
    IF NEW.date < CURRENT_DATE THEN
        NEW.action := 'archived';
    END IF;

    -- Ensure all older reservations are archived
    UPDATE RoomReservations
    SET action = 'archived'
    WHERE date < CURRENT_DATE
      AND action = 'active';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION accept_task(p_task_id INTEGER, p_user_id INTEGER)
    RETURNS BOOLEAN AS
$$
BEGIN
    UPDATE Tasks
    SET status     = 'in progress',
        updated_at = CURRENT_TIMESTAMP
    WHERE task_id = p_task_id
      AND status = 'pending'
      AND EXISTS (SELECT 1
                  FROM TaskAssignments
                  WHERE task_id = p_task_id
                    AND user_id = p_user_id);

    IF FOUND THEN
        RETURN TRUE; -- Task updated
    ELSE
        RETURN FALSE; -- Not updated
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION complete_task(p_task_id INTEGER, p_user_id INTEGER)
    RETURNS BOOLEAN AS
$$
BEGIN
    UPDATE Tasks
    SET status       = 'completed',
        completed_at = CURRENT_TIMESTAMP,
        updated_at   = CURRENT_TIMESTAMP
    WHERE task_id = p_task_id
      AND status = 'in progress'
      AND EXISTS (SELECT 1
                  FROM TaskAssignments
                  WHERE task_id = p_task_id
                    AND user_id = p_user_id);

    IF FOUND THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_overdue_tasks()
    RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.status IN ('pending', 'in progress') AND NEW.due_date < CURRENT_DATE THEN
        NEW.status := 'overdue';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_inventory(
    p_item_id INTEGER,
    p_new_quantity INTEGER,
    p_performed_by INTEGER
)
RETURNS TEXT AS
$$
DECLARE
    v_old_quantity INTEGER;
    v_reorder_level INTEGER;
    v_item_name TEXT;
    v_quantity_change INTEGER;
    v_action inventory_action;
BEGIN
    -- Fetch the current details of the item
    SELECT quantity, reorder_level, name
    INTO v_old_quantity, v_reorder_level, v_item_name
    FROM InventoryItems
    WHERE item_id = p_item_id;

    IF NOT FOUND THEN
        RETURN 'Item not found';
    END IF;

    -- Calculate the change in quantity
    v_quantity_change := p_new_quantity - v_old_quantity;

    -- Determine the action type
    v_action := CASE
                    WHEN v_quantity_change >= 0 THEN 'restocked'
                    ELSE 'expired'
                END;

    -- Update the inventory item quantity
    UPDATE InventoryItems
    SET quantity = p_new_quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE item_id = p_item_id;

    -- Log the inventory action
    INSERT INTO InventoryLogs (item_id, action, quantity_change, performed_by, action_date)
    VALUES (p_item_id, v_action, v_quantity_change, p_performed_by, CURRENT_TIMESTAMP);

    -- If the quantity is below the reorder level, create a low-stock task
    IF p_new_quantity < v_reorder_level THEN
        PERFORM create_low_stock_task(v_item_name, p_item_id, v_reorder_level, p_new_quantity);
    END IF;

    RETURN 'Inventory updated successfully';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_low_stock_task(
    p_item_name TEXT,
    p_item_id INTEGER,
    p_reorder_level INTEGER,
    p_current_quantity INTEGER
)
RETURNS VOID AS
$$
DECLARE
    v_task_id INTEGER;
BEGIN
    -- Insert a new task for low stock
    INSERT INTO Tasks (
        task_name,
        task_description,
        due_date,
        task_type_id,
        priority,
        created_by
    )
    VALUES (
        CONCAT('LOW STOCK - ', p_item_name),
        CONCAT(
            'Item "', p_item_name,
            '" is below reorder level! Current qty: ', p_current_quantity,
            ', reorder level: ', p_reorder_level, '. Refill needed.'
        ),
        CURRENT_DATE,
        1, -- Assuming "1" is the task type ID for low stock
        'high',
        0 -- Created by system
    )
    RETURNING task_id INTO v_task_id;

    -- Assign the task to all technicians
    INSERT INTO TaskAssignments (task_id, user_id)
    SELECT v_task_id, user_id
    FROM Users
    WHERE role = 'technician';
END;
$$ LANGUAGE plpgsql;