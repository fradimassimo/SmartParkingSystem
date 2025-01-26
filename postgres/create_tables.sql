CREATE TABLE parkings (
    parking_id VARCHAR(50) PRIMARY KEY,   
    name VARCHAR(100) NOT NULL,      -- Parking name
    latitude FLOAT NOT NULL,         
    longitude FLOAT NOT NULL,        
    paying_hours VARCHAR(50),        -- Hours during which payment is required
    price_per_hour FLOAT,            -- Price per hour
    parking_type VARCHAR(10) NOT NULL  -- 'street' or 'covered'
);

CREATE TABLE occupancy_data (
    parking_id VARCHAR(50) NOT NULL,                -- References parkings table
    timestamp TIMESTAMP NOT NULL,           -- Timestamp for the record
    occupancy INT,                          -- Occupancy count
    vacancy INT,                            -- Vacancy count
    PRIMARY KEY (parking_id, timestamp),    -- The primary key consists of the combination of the parking and the timestamp
    FOREIGN KEY (parking_id) REFERENCES parkings(parking_id)
);
