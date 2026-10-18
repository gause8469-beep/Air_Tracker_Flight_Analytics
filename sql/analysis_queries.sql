-- 1. Count flights by aircraft model
SELECT
    aircraft.model,
    COUNT(flights.flight_id) AS total_flights
FROM flights
JOIN aircraft
    ON flights.aircraft_registration = aircraft.registration
GROUP BY aircraft.model
ORDER BY total_flights DESC;

-- 2. Find aircraft that appear on more than five flights
SELECT
    aircraft.registration,
    aircraft.model,
    COUNT(flights.flight_id) AS total_flights
FROM aircraft
JOIN flights
    ON flights.aircraft_registration = aircraft.registration
GROUP BY aircraft.registration, aircraft.model
HAVING COUNT(flights.flight_id) > 5
ORDER BY total_flights DESC;

-- 3. Find airports with more than five departing flights
SELECT
    airport.iata_code,
    airport.name,
    COUNT(flights.flight_id) AS departing_flights
FROM airport
JOIN flights
    ON flights.origin_iata = airport.iata_code
GROUP BY airport.iata_code, airport.name
HAVING COUNT(flights.flight_id) > 5
ORDER BY departing_flights DESC;

-- 4. Show the three airports with the most arriving flights
SELECT
    airport.iata_code,
    airport.name,
    COUNT(flights.flight_id) AS arriving_flights
FROM airport
JOIN flights
    ON flights.destination_iata = airport.iata_code
GROUP BY airport.iata_code, airport.name
ORDER BY arriving_flights DESC
LIMIT 3;

-- 5. Classify flights as domestic or international
SELECT
    flights.flight_id,
    origin.iata_code AS origin,
    destination.iata_code AS destination,
    CASE
        WHEN origin.country IS NULL OR destination.country IS NULL THEN 'Unknown'
        WHEN origin.country = destination.country THEN 'Domestic'
        ELSE 'International'
    END AS flight_type
FROM flights
JOIN airport AS origin
    ON flights.origin_iata = origin.iata_code
JOIN airport AS destination
    ON flights.destination_iata = destination.iata_code;

-- 6. Show the five most recent scheduled arrivals at DEL
SELECT
    flight_id,
    flight_number,
    airline_code,
    origin_iata,
    scheduled_arrival,
    status
FROM flights
WHERE destination_iata = 'DEL'
ORDER BY scheduled_arrival DESC
LIMIT 5;

-- 7. Find airports with no recorded arrivals
SELECT
    airport.iata_code,
    airport.name
FROM airport
LEFT JOIN flights
    ON flights.destination_iata = airport.iata_code
WHERE flights.flight_id IS NULL
ORDER BY airport.iata_code;

-- 8. Count flights by airline and status
SELECT
    airline_code,
    status,
    COUNT(*) AS flight_count
FROM flights
GROUP BY airline_code, status
ORDER BY airline_code, status;

-- 9. List canceled flights
SELECT
    flight_id,
    flight_number,
    airline_code,
    origin_iata,
    destination_iata,
    status
FROM flights
WHERE LOWER(status) IN ('canceled', 'cancelled')
ORDER BY flight_id;

-- 10. Find routes flown by more than two aircraft models
SELECT
    origin.city AS origin_city,
    destination.city AS destination_city,
    COUNT(DISTINCT aircraft.model) AS different_models
FROM flights
JOIN airport AS origin
    ON flights.origin_iata = origin.iata_code
JOIN airport AS destination
    ON flights.destination_iata = destination.iata_code
JOIN aircraft
    ON flights.aircraft_registration = aircraft.registration
GROUP BY origin.city, destination.city
HAVING COUNT(DISTINCT aircraft.model) > 2
ORDER BY different_models DESC;

-- 11. Calculate the delayed-flight percentage for each destination
SELECT
    destination_iata,
    COUNT(*) AS total_flights,
    SUM(CASE WHEN LOWER(status) = 'delayed' THEN 1 ELSE 0 END) AS delayed_flights,
    ROUND(
        100.0 * SUM(CASE WHEN LOWER(status) = 'delayed' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS delayed_percentage
FROM flights
GROUP BY destination_iata
ORDER BY delayed_percentage DESC;

