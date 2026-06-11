// server.js (Updated Endpoint)
const express = require('express');
const { Pool } = require('pg');
const bodyParser = require('body-parser');

const app = express();
const port = 5000;

app.use(bodyParser.json());

const pool = new Pool({
    user: 'your_db_user',
    host: 'localhost',
    database: 'alpr_db',
    password: 'your_db_password',
    port: 5432,
});

app.post('/api/check-arrival', async (req, res) => {
    const { license_plate } = req.body;

    if (!license_plate) {
        return res.status(400).json({ error: 'License plate text is missing.' });
    }

    console.log(`[Arrival Trigger] Checking plate: ${license_plate}`);

    try {
        // Query includes apartment_number and allotted_parking_slot
        const result = await pool.query(
            `SELECT owner_name, apartment_number, allotted_parking_slot 
       FROM registered_vehicles 
       WHERE license_plate = $1 AND status = $2`,
            [license_plate.toUpperCase(), 'active']
        );

        if (result.rows.length > 0) {
            const vehicle = result.rows[0];

            console.log(`[ACCESS GRANTED] Resident: ${vehicle.owner_name} | Apt: ${vehicle.apartment_number} | Parking: ${vehicle.allotted_parking_slot}`);

            // Optional: Update parking status to 'IN' since the car just arrived
            await pool.query(
                'UPDATE registered_vehicles SET parking_status = $1 WHERE license_plate = $2',
                ['IN', license_plate.toUpperCase()]
            );

            // Return comprehensive data back to the edge client
            res.json({
                registered: true,
                owner_name: vehicle.owner_name,
                apartment_number: vehicle.apartment_number,
                allotted_parking_slot: vehicle.allotted_parking_slot
            });
        } else {
            console.log(`[ACCESS DENIED] Plate ${license_plate} is not registered.`);
            res.json({ registered: false });
        }

    } catch (error) {
        console.error('Database query error:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(port, '0.0.0.0', () => {
    console.log(`ALPR Server listening at http://0.0.0.0:${port}`);
});