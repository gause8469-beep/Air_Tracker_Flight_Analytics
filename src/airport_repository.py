from db_connection import get_connection


def save_airport(airport):
    columns = (
        "icao_code",
        "iata_code",
        "name",
        "city",
        "country",
        "continent",
        "latitude",
        "longitude",
        "timezone",
    )

    values = tuple(airport.get(column) for column in columns)

    query = """
        INSERT INTO airport (
            icao_code, iata_code, name, city, country, continent,
            latitude, longitude, timezone
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            city = VALUES(city),
            country = VALUES(country),
            continent = VALUES(continent),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude),
            timezone = VALUES(timezone)
    """

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

