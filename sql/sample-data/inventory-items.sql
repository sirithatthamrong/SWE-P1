INSERT INTO InventoryItems (category_id, name, quantity, reorder_level, expiration_date, supplier_id)
VALUES
    (1, 'Microscope', 10, 2, NULL, 1),
    (1, 'Centrifuge', 5, 1, NULL, 2),
    (2, 'Ethanol', 50, 10, '2025-12-31', 3),
    (2, 'Acetone', 30, 5, '2025-11-15', 3),
    (3, 'Printer Paper', 500, 100, NULL, 4),
    (4, 'Safety Goggles', 20, 5, NULL, 5),
    (5, 'Beaker Set', 15, 3, NULL, 1);