from db_connection import get_connection


def save_aircraft(aircraft):
    """Insert or update an aircraft record when it has a registration."""
    if not aircraft or not aircraft.get("registration"):
        return False

    query = """
        INSERT INTO aircraft (
            registration, model, manufacturer, icao_type_code, owner
        )
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            model = VALUES(model),
            manufacturer = VALUES(manufacturer),
            icao_type_code = VALUES(icao_type_code),
            owner = VALUES(owner)
    """

    values = (
        aircraft.get("registration"),
        aircraft.get("model"),
        aircraft.get("manufacturer"),
        aircraft.get("icao_type_code"),
        aircraft.get("owner"),
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

    return True
