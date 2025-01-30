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
    p_performed_by INTEGER,
    p_expiration_date DATE DEFAULT NULL
)
    RETURNS TEXT AS
$$
DECLARE
    v_batch_id         INTEGER;
    v_old_qty          INTEGER;
    v_use_date         DATE;
    v_total_qty        INTEGER;
    v_reorder_level    INTEGER;
    v_task_id          INTEGER;
    -- For the supplier/task info:
    v_item_name        VARCHAR;
    v_supplier_name    VARCHAR;
    v_supplier_contact TEXT;
    v_task_type_id     INTEGER;
BEGIN
    -- Normalize expiration date
    IF p_expiration_date IS NULL OR p_expiration_date = '9999-12-31' THEN
        v_use_date := '9999-12-31';
    ELSE
        v_use_date := p_expiration_date;
    END IF;

    -- 1) Fetch item info (including reorder_level and supplier)
    SELECT i.name, i.reorder_level, s.supplier_name, s.contact_info
    INTO v_item_name, v_reorder_level, v_supplier_name, v_supplier_contact
    FROM InventoryItems i
             LEFT JOIN Suppliers s ON i.supplier_id = s.supplier_id
    WHERE i.item_id = p_item_id
    LIMIT 1;

    -- If item not found, return an error
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Item ID % does not exist', p_item_id;
    END IF;

    -- 2) Ensure batch exists, then replace quantity
    SELECT batch_id, quantity
    INTO v_batch_id, v_old_qty
    FROM InventoryBatches
    WHERE item_id = p_item_id
      AND expiration_date = v_use_date
        FOR UPDATE;

    IF FOUND THEN
        -- Replace quantity instead of adding
        UPDATE InventoryBatches
        SET quantity = p_new_quantity
        WHERE batch_id = v_batch_id;
    ELSE
        -- Insert new batch if not found
        INSERT INTO InventoryBatches (item_id, quantity, expiration_date)
        VALUES (p_item_id, p_new_quantity, v_use_date)
        RETURNING batch_id INTO v_batch_id;
    END IF;

    -- 3) Recalculate total quantity
    SELECT COALESCE(SUM(quantity), 0)
    INTO v_total_qty
    FROM InventoryBatches
    WHERE item_id = p_item_id;

    -- 4) Log the restocking action
    INSERT INTO InventoryLogs (item_id, action, quantity_change, performed_by, action_date)
    VALUES (p_item_id, 'restocked', p_new_quantity, p_performed_by, CURRENT_TIMESTAMP);

    -- 5) If stock falls below reorder level, create a "RESTOCK (item_name)" task if none exists
    IF v_total_qty <= v_reorder_level THEN
        -- Optional: If you only want to do this if the reorder_level is > 0,
        -- you could add: IF v_reorder_level > 0 THEN ... END IF;

        -- Check if we already have a pending/in-progress "RESTOCK (item name)" task
        SELECT task_id
        INTO v_task_id
        FROM Tasks
        WHERE task_name = 'RESTOCK - ' || v_item_name
          AND status IN ('pending', 'in progress')
        LIMIT 1;

        IF v_task_id IS NULL THEN
            -- Make sure we find the 'Restock' task_type_id
            SELECT task_type_id
            INTO v_task_type_id
            FROM TaskTypes
            WHERE task_name = 'Restock'
            LIMIT 1;

            IF v_task_type_id IS NULL THEN
                RAISE EXCEPTION 'No TaskTypes row found for ''Restock''!';
            END IF;

            INSERT INTO Tasks (task_name,
                               task_description,
                               due_date,
                               task_type_id,
                               priority,
                               created_by)
            VALUES ('RESTOCK - ' || v_item_name,
                    'Item "' || v_item_name || '" is below reorder level!'
                        || ' Current qty: ' || v_total_qty
                        || ', reorder level: ' || v_reorder_level
                        || CASE
                               WHEN v_supplier_name IS NOT NULL THEN
                                   E'\nSupplier: ' || v_supplier_name
                                       || E'\nContact: ' || v_supplier_contact
                               ELSE
                                   ''
                        END,
                    CURRENT_DATE + INTERVAL '1 day',
                    v_task_type_id,
                    'high',
                    0 -- 0 can signify "system user"
                   )
            RETURNING task_id INTO v_task_id;

            -- Assign task to all technicians
            INSERT INTO TaskAssignments (task_id, user_id)
            SELECT v_task_id, user_id
            FROM Users
            WHERE role = 'technician';
        END IF;
    END IF;

    RETURN 'Inventory updated successfully';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_tasks_for_user(p_user_id INT)
RETURNS TABLE
        (
            task_id          INT,
            task_name        TEXT,
            task_description TEXT,
            due_date         DATE,
            priority         TEXT,
            status           TEXT,
            created_at       TIMESTAMP,
            updated_at       TIMESTAMP,
            created_by       INT,
            creator_name     TEXT,
            task_type        TEXT
        )
AS
$$
BEGIN
    RETURN QUERY
    SELECT t.task_id,
           t.task_name::TEXT,
           t.task_description,
           t.due_date,
           t.priority::TEXT,
           t.status::TEXT,
           t.created_at,
           t.updated_at,
           t.created_by,
           u.username::TEXT AS creator_name,
           tt.task_name::TEXT AS task_type
    FROM Tasks t
    JOIN TaskTypes tt ON t.task_type_id = tt.task_type_id
    JOIN TaskAssignments ta ON ta.task_id = t.task_id
    JOIN Users u ON t.created_by = u.user_id
    WHERE ta.user_id = p_user_id
    ORDER BY
        CASE WHEN t.status = 'overdue' THEN 1 ELSE 2 END,
        t.due_date ASC;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION request_role_verification(
    p_user_id INT,
    p_requested_role VARCHAR
) RETURNS VOID AS
$$
BEGIN
    -- Only allow role requests for 'technician' or 'researcher'
    IF p_requested_role NOT IN ('technician', 'researcher') THEN
        RAISE EXCEPTION 'Invalid role request!';
    END IF;

    -- Update the user with the requested role
    UPDATE Users
    SET requested_role = p_requested_role
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;
