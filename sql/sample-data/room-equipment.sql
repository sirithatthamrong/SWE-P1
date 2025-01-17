INSERT INTO RoomEquipment (lab_room_id, equipment_id, quantity, equipment_status) VALUES
-- Molecular Analysis Lab
(1, 1, 5, 'available'),  -- Microscopes
(1, 3, 2, 'available'),  -- PCR Machine
(1, 9, 1, 'available'),  -- Thermocycler

-- Structural Analysis Lab
(13, 14, 1, 'available'),  -- Tensile Testing Machine
(13, 12, 2, 'available'),  -- X-Ray Diffractometer

-- Chemical Process Lab
(36, 5, 1, 'available'),   -- Gas Chromatograph
(36, 19, 1, 'available'),  -- Mass Spectrometer

-- Cybersecurity Lab (No physical lab equipment required)

-- Optics and Lasers Lab
(6, 6, 2, 'available'),  -- Laser Cutter
(6, 20, 1, 'available'); -- UV-Vis Spectrometer
