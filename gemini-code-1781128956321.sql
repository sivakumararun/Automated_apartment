CREATE TABLE registered_vehicles (
    id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    owner_name VARCHAR(100),
    vehicle_model VARCHAR(100),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) DEFAULT 'active' -- 'active' or 'suspended'
);

-- Sample Data
INSERT INTO registered_vehicles (license_plate, owner_name) 
VALUES ('CALIF123', 'John Doe'), ('TEXAS888', 'Jane Smith');