CREATE TABLE registered_vehicles (
    id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    apartment_number VARCHAR(10) NOT NULL,    -- Tracks the resident's apartment
    allotted_parking_slot VARCHAR(20) NOT NULL, -- Tracks the assigned parking bay
    vehicle_model VARCHAR(100),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) DEFAULT 'active',        -- 'active' or 'suspended'
    parking_status VARCHAR(15) DEFAULT 'OUT'   -- 'IN' or 'OUT' (for tracking presence)
);

-- Sample Data representing apartment residents
INSERT INTO registered_vehicles (license_plate, owner_name, apartment_number, allotted_parking_slot) 
VALUES 
('CALIF123', 'John Doe', 'Apt 4B', 'Slot-042'), 
('TEXAS888', 'Jane Smith', 'Apt 12C', 'Slot-105');