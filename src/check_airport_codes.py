import csv
from pathlib import Path

csv_path = Path(__file__).resolve().parent.parent / "data" / "airport_codes.csv"

with csv_path.open(newline="", encoding="utf-8") as file:
    codes = [row["iata_code"].strip().upper() for row in csv.DictReader(file)]

print(f"Airport codes found: {len(codes)}")
print(f"Unique codes found: {len(set(codes))}")
print(", ".join(codes))

