// server.js - Running on the backend
const express = require('express');
const { Pool } = require('pg');
const bodyParser = require('body-parser');

const app = express();
const port = 5000;

// Middleware
app.use(bodyParser.json());

// Database connection configuration
const pool = new Pool({
  user: 'your_db_user',
  host: 'localhost',
  database: 'alpr_db',
  password: 'your_db_password',
  port: 5432,
});

// Primary Endpoint for Client
app.post('/api/check-arrival', async (req, res) => {
  const { license_plate } = req.body;

  if (!license_plate) {
    return res.status(400).json({ error: 'License plate text is missing.' });
  }

  console.log(`Checking registration for: ${license_plate}`);

  try {
    // Basic EXACT MATCH. (In production, use ILIKE/fuzzy matching)
    const result = await pool.query(
      'SELECT owner_name FROM registered_vehicles WHERE license_plate = $1 AND status = $2',
      [license_plate.toUpperCase(), 'active']
    );

    if (result.rows.length > 0) {
      const owner = result.rows[0].owner_name;
      console.log(`Match Found! Authorized entry for ${owner}.`);
      res.json({ registered: true, owner_name: owner });
    } else {
      console.log(`No match found for ${license_plate}.`);
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