# Air Tracker Flight Analytics

A beginner-level data analytics project that combines airport reference data, flight records, MySQL, SQL analysis, and a Streamlit dashboard.

## What the project does

- Stores airports, aircraft, flights, and airport delay information in a relational MySQL database.
- Runs 11 SQL queries for flight, airport, route, status, and delay analysis.
- Displays airport and flight summaries, charts, and report tables in Streamlit.
- Uses AeroDataBox airport flight information through RapidAPI for a limited flight snapshot.

## Current project snapshot

The dashboard combines airport reference data with flight snapshots fetched from AeroDataBox through RapidAPI. The importer keeps records that match the selected airport reference list and skips incomplete or out-of-scope records. API responses are temporary; this repository does not include flight records, API response files, or dashboard exports containing flight data.

## Project structure

```text
Air_Tracker_Flight_Analytics/
├── app.py                       # Streamlit dashboard
├── data/
│   ├── airport_codes.csv        # Airports requested by the importer
│   ├── airports.csv             # Airport reference data for MySQL
│   └── flights_template.csv     # Optional CSV import template
├── docs/
│   └── project_report.md        # Project summary and limitations
├── sql/
│   ├── schema.sql               # Database tables and relationships
│   └── analysis_queries.sql     # 11 SQL analytics queries
├── outputs/                     # Local-only screenshots and presentation (excluded from Git)
└── src/
    ├── fetch_live_flights.py    # Bounded AeroDataBox importer
    ├── import_airports.py       # Airport CSV importer
    ├── import_flights.py        # Flight CSV importer
    └── ...                      # API, repository, and normalization modules
```

## Submission files

- Dashboard screenshots and the presentation are kept locally for course submission.
- They are excluded from this GitHub repository because they contain temporary API flight information.

## Setup

1. Start the MySQL server and create the `air_tracker` schema by running `sql/schema.sql` in MySQL Workbench.
2. Create a `.env` file in this project folder with your MySQL connection settings and RapidAPI credentials. Keep this file private and do not upload it.
3. Install the packages in `requirements.txt` inside your virtual environment:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Import the airport reference CSV:

   ```powershell
   .\.venv\Scripts\python.exe src\import_airports.py
   ```

5. Run the dashboard:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

   Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Flight data and quota

The API importer uses the AeroDataBox airport FIDS endpoint, which is a Tier-2 endpoint. The script makes one request per selected airport, runs sequentially, and does not retry failed calls. Use `--airport DEL` to request one airport only:

```powershell
.\.venv\Scripts\python.exe src\fetch_live_flights.py --airport DEL
```

Without `--airport`, the script can request up to the 15 airport codes in `data/airport_codes.csv`. Check your RapidAPI quota before running a multi-airport collection. Coverage and returned fields vary by airport; an API request may return no usable records.

AeroDataBox's free-plan terms require visible attribution and restrict retention of API content. The dashboard links to AeroDataBox. Treat API flight records as a temporary snapshot and remove them within the permitted retention period stated in the [AeroDataBox terms](https://aerodatabox.com/terms). The importer does not automatically expire or delete records.

## Analysis queries

Open `sql/analysis_queries.sql` in MySQL Workbench and run the queries individually or as a script. They cover aircraft models, busy airports, domestic and international routes, airline statuses, canceled and delayed flights, and airports with no recorded arrivals.

## Limitations

- The dashboard reflects the records currently in the local MySQL database; it does not automatically refresh data from AeroDataBox.
- The current flight sample was collected for DEL and limited to routes whose two airports are in the 15-airport reference table.
- Some charts use only flights with aircraft information. Missing aircraft details can make their totals lower than the total flight count.
- Status and delay analyses describe the collected snapshot and should not be interpreted as long-term performance statistics.




