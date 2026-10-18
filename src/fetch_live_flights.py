"""Fetch one small, bounded AeroDataBox FIDS snapshot for the project airports."""

import csv
import argparse
from pathlib import Path

from api_client import get_json
from aircraft_repository import save_aircraft
from db_connection import get_connection
from flight_repository import save_flight
from normalize_flight import normalize_flight


MAX_AIRPORTS_PER_RUN = 15
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_airport_codes():
    path = PROJECT_ROOT / "data" / "airport_codes.csv"
    with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        codes = [
            (row.get("iata_code") or "").strip().upper()
            for row in csv.DictReader(csv_file)
        ]
    codes = [code for code in codes if len(code) == 3 and code.isalpha()]
    if not codes:
        raise ValueError("No valid IATA codes were found in data/airport_codes.csv.")
    if len(codes) > MAX_AIRPORTS_PER_RUN:
        raise ValueError(
            f"This safe run is capped at {MAX_AIRPORTS_PER_RUN} airport calls; "
            f"the CSV currently contains {len(codes)} airports."
        )
    return list(dict.fromkeys(codes))


def extract_flights(payload):
    if payload is None:
        return []
    if not isinstance(payload, dict):
        raise ValueError("Unexpected AeroDataBox response format (expected an object).")
    return (
        [(flight, "departure") for flight in (payload.get("departures") or [])]
        + [(flight, "arrival") for flight in (payload.get("arrivals") or [])]
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--airport",
        help="Fetch only this one IATA airport (one Tier-2 request).",
    )
    args = parser.parse_args()
    airport_codes = load_airport_codes()
    if args.airport:
        code = args.airport.strip().upper()
        if code not in airport_codes:
            raise ValueError("Choose an airport listed in data/airport_codes.csv.")
        airport_codes = [code]
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT iata_code, icao_code FROM airport")
        airport_rows = cursor.fetchall()
        known_airports = {row[0] for row in airport_rows}
        icao_to_iata = {
            icao.upper(): iata
            for iata, icao in airport_rows
            if iata and icao
        }
    finally:
        cursor.close()
        connection.close()

    saved_ids = set()
    malformed = 0
    out_of_scope = 0
    malformed_reasons = {}
    print(
        f"Starting one pass: at most {len(airport_codes)} Tier-2 airport requests; "
        "no retries."
    )

    for index, code in enumerate(airport_codes, start=1):
        print(f"Request {index}/{len(airport_codes)}: {code}")
        payload = get_json(
            f"flights/airports/iata/{code}",
            params={"withLeg": "true"},
        )
        for raw_flight, direction in extract_flights(payload):
            try:
                flight = normalize_flight(
                    raw_flight,
                    observed_airport=code,
                    direction=direction,
                    icao_to_iata=icao_to_iata,
                )
            except (TypeError, ValueError) as error:
                malformed += 1
                reason = str(error) or type(error).__name__
                malformed_reasons[reason] = malformed_reasons.get(reason, 0) + 1
                continue

            if (
                flight["origin_iata"] not in known_airports
                or flight["destination_iata"] not in known_airports
            ):
                out_of_scope += 1
                continue

            save_aircraft(flight.pop("aircraft"))
            save_flight(flight)
            saved_ids.add(flight["flight_id"])

    print(
        f"Finished. Saved or refreshed {len(saved_ids)} unique flights; "
        f"skipped {malformed} incomplete records and {out_of_scope} routes "
        "outside the airport table."
    )
    if malformed_reasons:
        print("Normalization skip reasons:")
        for reason, count in sorted(
            malformed_reasons.items(), key=lambda item: item[1], reverse=True
        ):
            print(f"  {count}: {reason}")
    print("Delete this API snapshot within 7 days, as required by the Basic-plan terms.")


if __name__ == "__main__":
    main()
