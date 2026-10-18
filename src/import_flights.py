import csv
from datetime import datetime
from pathlib import Path

from flight_repository import save_flight


DATETIME_FIELDS = (
    "scheduled_departure",
    "actual_departure",
    "scheduled_arrival",
    "actual_arrival",
)


def _parse_datetime(value, field_name):
    value = (value or "").strip()
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"Invalid {field_name}: {value!r}. Use YYYY-MM-DD HH:MM:SS."
        ) from error


def import_flights():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "flights_template.csv"
    imported_count = 0

    with csv_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        for line_number, row in enumerate(csv.DictReader(csv_file), start=2):
            flight = {
                key: (value or "").strip() or None
                for key, value in row.items()
            }

            if not flight.get("flight_id"):
                raise ValueError(f"Row {line_number} is missing flight_id.")
            if not flight.get("origin_iata") or not flight.get("destination_iata"):
                raise ValueError(
                    f"Row {line_number} needs origin_iata and destination_iata."
                )

            flight["origin_iata"] = flight["origin_iata"].upper()
            flight["destination_iata"] = flight["destination_iata"].upper()
            for field_name in DATETIME_FIELDS:
                flight[field_name] = _parse_datetime(
                    flight.get(field_name), field_name
                )

            save_flight(flight)
            imported_count += 1

    print(f"Flight CSV import completed. Rows imported: {imported_count}")


if __name__ == "__main__":
    import_flights()
