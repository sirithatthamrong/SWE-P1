CREATE TYPE user_role AS ENUM ('admin', 'technician', 'user', 'researcher');
CREATE TYPE equipment_status AS ENUM ('available', 'needs maintenance');
CREATE TYPE reservation_action AS ENUM ('active', 'canceled', 'archived');
CREATE TYPE inventory_action AS ENUM ('restocked', 'expired');
CREATE TYPE maintenance_status AS ENUM ('scheduled', 'completed', 'overdue');
CREATE TYPE task_required_role AS ENUM ( 'admin', 'technician','user', 'researcher');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high');
CREATE TYPE task_status AS ENUM ('pending', 'in progress', 'completed', 'overdue');

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE Users
(
    user_id              SERIAL PRIMARY KEY,
    username             VARCHAR(100) NOT NULL UNIQUE,
    email                VARCHAR(100) NOT NULL,
    password             TEXT         NOT NULL,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role                 user_role DEFAULT 'user',
    notification_enabled BOOLEAN   DEFAULT TRUE
);

CREATE TABLE LabZones
(
    lab_zone_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE LabRooms
(
    lab_room_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    lab_zone_id INTEGER NOT NULL,
    location VARCHAR(100) NOT NULL,
    FOREIGN KEY (lab_zone_id) REFERENCES LabZones(lab_zone_id) ON DELETE CASCADE
);

CREATE TABLE EquipmentTypes
(
    equipment_id SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ExperimentTypes
(
    experiment_id SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ExperimentEquipment
(
    experiment_id INTEGER NOT NULL,
    equipment_id  INTEGER NOT NULL,
    PRIMARY KEY (experiment_id, equipment_id),
    FOREIGN KEY (experiment_id) REFERENCES ExperimentTypes (experiment_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES EquipmentTypes (equipment_id) ON DELETE CASCADE
);

CREATE TABLE RoomEquipment
(
    lab_room_id      INTEGER NOT NULL,
    equipment_id     INTEGER NOT NULL,
    quantity         INTEGER NOT NULL CHECK (quantity >= 0),
    equipment_status equipment_status DEFAULT 'available',
    PRIMARY KEY (lab_room_id, equipment_id),
    FOREIGN KEY (lab_room_id) REFERENCES LabRooms (lab_room_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES EquipmentTypes (equipment_id) ON DELETE CASCADE
);

CREATE TABLE RoomReservations
(
    reservation_id SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL,
    lab_zone_id    INTEGER NOT NULL,
    lab_room_id    INTEGER NOT NULL,
    experiment_id  INTEGER,
    date           DATE    NOT NULL,
    start_time     TIME    NOT NULL,
    end_time       TIME    NOT NULL,
    action         reservation_action NOT NULL DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (lab_zone_id) REFERENCES LabZones (lab_zone_id) ON DELETE CASCADE,
    FOREIGN KEY (lab_room_id) REFERENCES LabRooms (lab_room_id) ON DELETE CASCADE,
    FOREIGN KEY (experiment_id) REFERENCES ExperimentTypes (experiment_id) ON DELETE CASCADE,
    CHECK (start_time < end_time)
);

CREATE TABLE Suppliers
(
    supplier_id   SERIAL PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL UNIQUE,
    contact_info  TEXT
);

CREATE TABLE InventoryCategories
(
    category_id   SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE InventoryItems
(
    item_id         SERIAL PRIMARY KEY,
    category_id     INTEGER      NOT NULL,
    name            VARCHAR(100) NOT NULL,
    quantity        INTEGER      NOT NULL CHECK ( quantity >= 0 ),
    reorder_level   INTEGER      NOT NULL CHECK ( reorder_level >= 0 ),
    expiration_date DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    supplier_id     INTEGER,
    FOREIGN KEY (category_id) REFERENCES InventoryCategories (category_id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers (supplier_id)
);

CREATE TABLE InventoryLogs
(
    log_id          SERIAL PRIMARY KEY,
    item_id         INTEGER          NOT NULL,
    action          inventory_action NOT NULL,
    quantity_change INTEGER          NOT NULL,
    action_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performed_by    INTEGER,
    FOREIGN KEY (item_id) REFERENCES InventoryItems (item_id),
    FOREIGN KEY (performed_by) REFERENCES Users (user_id)
);

CREATE TABLE Maintenance
(
    maintenance_id SERIAL PRIMARY KEY,
    lab_id         INTEGER NOT NULL,
    equipment_id   INTEGER NOT NULL,
    schedule_date  DATE    NOT NULL,
    performed_by   INTEGER NOT NULL,
    status         maintenance_status DEFAULT 'scheduled',
    FOREIGN KEY (lab_id) REFERENCES LabRooms (lab_room_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES EquipmentTypes (equipment_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES Users (user_id)
);

CREATE TABLE MaintenanceLogs
(
    log_id         SERIAL PRIMARY KEY,
    maintenance_id INTEGER NOT NULL,
    action_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performed_by   INTEGER NOT NULL,
    FOREIGN KEY (maintenance_id) REFERENCES Maintenance (maintenance_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES Users (user_id)
);

CREATE TABLE Notifications
(
    notification_id SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    message         TEXT    NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Reports
(
    report_id   SERIAL PRIMARY KEY,
    lab_id      INTEGER NOT NULL,
    reported_by INTEGER NOT NULL,
    report_text TEXT    NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lab_id) REFERENCES LabRooms (lab_room_id) ON DELETE CASCADE,
    FOREIGN KEY (reported_by) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE TaskTypes
(
    task_type_id  SERIAL PRIMARY KEY,
    task_name     VARCHAR(100)       NOT NULL UNIQUE,
    required_role task_required_role NOT NULL
);

CREATE TABLE Tasks
(
    task_id          SERIAL PRIMARY KEY,
    task_name        VARCHAR(100) NOT NULL,
    task_description TEXT         NOT NULL,
    due_date         DATE         NOT NULL CHECK ( due_date >= CURRENT_DATE ),
    task_type_id     INTEGER      NOT NULL,
    created_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    priority         task_priority DEFAULT 'medium',
    status           task_status   DEFAULT 'pending',
    completed_at     TIMESTAMP,
    created_by       INTEGER      NOT NULL,
    FOREIGN KEY (created_by) REFERENCES Users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_type_id) REFERENCES TaskTypes (task_type_id) ON DELETE CASCADE
);

CREATE TABLE TaskAssignments
(
    assignment_id SERIAL PRIMARY KEY,
    task_id       INTEGER NOT NULL,
    user_id       INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES Tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    UNIQUE (task_id, user_id)
);

CREATE TABLE TaskLogs
(
    log_id       SERIAL PRIMARY KEY,
    task_id      INTEGER NOT NULL,
    action_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performed_by INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES Tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES Users (user_id)
);

