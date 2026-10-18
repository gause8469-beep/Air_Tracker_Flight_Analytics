def normalize_aircraft(aircraft):
    """Convert aircraft details from a flight record into database columns."""
    aircraft = aircraft or {}
    registration = aircraft.get("reg")

    if not registration:
        return None

    return {
        "registration": registration,
        "model": aircraft.get("model") or aircraft.get("modelCode"),
        "manufacturer": aircraft.get("manufacturer"),
        "icao_type_code": aircraft.get("icaoCode") or aircraft.get("icaoTypeCode"),
        "owner": aircraft.get("owner"),
    }

