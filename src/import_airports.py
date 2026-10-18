import csv
from pathlib import Path

from airport_repository import save_airport


def import_airports():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "airports.csv"

    with csv_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            airport = {
                key: value.strip() or None
                for key, value in row.items()
            }
            save_airport(airport)

    print("Airport CSV import completed.")


if __name__ == "__main__":
    import_airports()
