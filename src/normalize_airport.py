def normalize_airport(airport):
    location = airport.get("location") or {}
    country = airport.get("country") or {}
    continent = airport.get("continent") or {}

    name = airport.get("fullName")
    if not name:
        raise ValueError("Airport response is missing its full name.")

    return {
        "icao_code": airport.get("icao"),
        "iata_code": airport.get("iata"),
        "name": name,
        "city": airport.get("municipalityName"),
        "country": country.get("name"),
        "continent": continent.get("name"),
        "latitude": location.get("lat"),
        "longitude": location.get("lon"),
        "timezone": airport.get("timeZone"),
    }

