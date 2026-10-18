from db_connection import get_connection


def save_flight(flight):
    query = """
        INSERT INTO flights (
            flight_id, flight_number, aircraft_registration,
            origin_iata, destination_iata,
            scheduled_departure, actual_departure,
            scheduled_arrival, actual_arrival,
            status, airline_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            status = VALUES(status),
            actual_departure = VALUES(actual_departure),
            actual_arrival = VALUES(actual_arrival)
    """

    values = (
        flight["flight_id"],
        flight["flight_number"],
        flight["aircraft_registration"],
        flight["origin_iata"],
        flight["destination_iata"],
        flight["scheduled_departure"],
        flight["actual_departure"],
        flight["scheduled_arrival"],
        flight["actual_arrival"],
        flight["status"],
        flight["airline_code"],
    )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query, values)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

