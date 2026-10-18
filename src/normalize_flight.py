from datetime import datetime, timezone
from normalize_aircraft import normalize_aircraft


def _iata_code(movement, icao_to_iata=None):
    airport = (movement or {}).get("airport") or {}
    iata = airport.get("iata")
    if iata:
        return iata.upper()
    icao = airport.get("icao")
    return (icao_to_iata or {}).get(icao.upper()) if icao else None


def _utc_datetime(movement, time_name):
    movement = movement or {}
    time_info = movement.get(time_name) or {}
    value = time_info.get("utc")

    if not value:
        return None

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


def normalize_flight(
    flight, observed_airport=None, direction=None, icao_to_iata=None
):
    departure = flight.get("departure") or {}
    arrival = flight.get("arrival") or {}

    # Without withLeg coverage, AeroDataBox supplies only the movement at
    # the requested airport and the opposite airport inside movement.airport.
    if not departure and not arrival and observed_airport:
        movement = flight.get("movement") or {}
        if direction == "departure":
            departure = {**movement, "airport": {"iata": observed_airport}}
            arrival = {"airport": movement.get("airport") or {}}
        elif direction == "arrival":
            departure = {"airport": movement.get("airport") or {}}
            arrival = {**movement, "airport": {"iata": observed_airport}}

    if observed_airport and direction == "departure":
        departure["airport"] = departure.get("airport") or {}
        departure["airport"].setdefault("iata", observed_airport)
    elif observed_airport and direction == "arrival":
        arrival["airport"] = arrival.get("airport") or {}
        arrival["airport"].setdefault("iata", observed_airport)

    origin_iata = _iata_code(departure, icao_to_iata)
    destination_iata = _iata_code(arrival, icao_to_iata)
    flight_number = (
        flight.get("number") or flight.get("flightNumber") or flight.get("callSign")
    )

    if not flight_number:
        raise ValueError("Flight number is missing.")
    if not origin_iata or not destination_iata:
        raise ValueError("Origin or destination IATA code is missing.")

    scheduled_departure = _utc_datetime(departure, "scheduledTime")
    scheduled_arrival = _utc_datetime(arrival, "scheduledTime")
    identity_time = scheduled_departure or scheduled_arrival

    if identity_time is None:
        raise ValueError("Flight is missing scheduled departure and arrival times.")

    flight_id = (
        f"{flight_number}|{origin_iata}|{destination_iata}|"
        f"{identity_time.strftime('%Y%m%dT%H%M%SZ')}"
    )

    aircraft = flight.get("aircraft") or {}
    airline = flight.get("airline") or {}

    return {
        "flight_id": flight_id,
        "flight_number": flight_number,
        "aircraft_registration": aircraft.get("reg"),
        "aircraft": normalize_aircraft(aircraft),
        "origin_iata": origin_iata,
        "destination_iata": destination_iata,
        "scheduled_departure": scheduled_departure,
        "actual_departure": None,
        "scheduled_arrival": scheduled_arrival,
        "actual_arrival": None,
        "status": flight.get("status"),
        "airline_code": airline.get("iata") or airline.get("icao"),
    }

