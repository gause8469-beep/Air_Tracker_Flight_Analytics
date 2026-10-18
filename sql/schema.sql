USE air_tracker;

CREATE TABLE IF NOT EXISTS airport (
    airport_id INT AUTO_INCREMENT PRIMARY KEY,
    icao_code VARCHAR(10) UNIQUE,
    iata_code VARCHAR(3) UNIQUE,
    name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    continent VARCHAR(50),
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    timezone VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id INT AUTO_INCREMENT PRIMARY KEY,
    registration VARCHAR(20) UNIQUE,
    model VARCHAR(100),
    manufacturer VARCHAR(100),
    icao_type_code VARCHAR(10),
    owner VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS flights (
    flight_id VARCHAR(100) PRIMARY KEY,
    flight_number VARCHAR(20),
    aircraft_registration VARCHAR(20),
    origin_iata VARCHAR(3) NOT NULL,
    destination_iata VARCHAR(3) NOT NULL,
    scheduled_departure DATETIME,
    actual_departure DATETIME,
    scheduled_arrival DATETIME,
    actual_arrival DATETIME,
    status VARCHAR(30),
    airline_code VARCHAR(10),
    FOREIGN KEY (aircraft_registration)
        REFERENCES aircraft(registration)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (origin_iata)
        REFERENCES airport(iata_code),
    FOREIGN KEY (destination_iata)
        REFERENCES airport(iata_code)
);

CREATE TABLE IF NOT EXISTS airport_delays (
    delay_id INT AUTO_INCREMENT PRIMARY KEY,
    airport_iata VARCHAR(3) NOT NULL,
    delay_date DATE,
    total_flights INT,
    delayed_flights INT,
    delay_index INT,
    median_delay_min INT,
    canceled_flights INT,
    FOREIGN KEY (airport_iata)
        REFERENCES airport(iata_code)
);

