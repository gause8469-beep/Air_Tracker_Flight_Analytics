# Air Tracker Flight Analytics — Project Report

## 1. Objective

The project demonstrates a beginner data-science workflow: prepare aviation reference data, store relational records in MySQL, analyze them with SQL, and present results in a Streamlit dashboard.

## 2. Tools and technologies

- Python for data handling, API requests, and the dashboard.
- MySQL for relational storage and querying.
- SQL for 11 analytical questions.
- Streamlit, pandas, and charts for the dashboard.
- AeroDataBox through RapidAPI as the flight information source.

## 3. Database design

The schema contains four tables:

- `airport`: airport codes, name, city, country, and reference details.
- `aircraft`: aircraft registration and model details.
- `flights`: flight number, route, times, status, airline, and aircraft registration.
- `airport_delays`: optional delay summary fields.

Foreign keys connect flights to their origin and destination airports and, when available, to an aircraft registration.

## 4. Data collection and preparation

Airport reference data is loaded from `data/airports.csv`. Flight records are requested from AeroDataBox's airport flight information endpoint and normalized into the project's MySQL schema. The importer makes bounded, sequential requests without retries. It only stores flights with both endpoints represented in the project's airport table.

During development, the importer was used to request a DEL airport flight snapshot. Coverage and completeness depend on the API response and airport reference list. This public repository intentionally excludes the returned flight records and all exports that show those records.

## 5. SQL analysis

The 11 queries examine:

1. Flight counts by aircraft model.
2. Aircraft appearing on more than five flights.
3. Airports with more than five departures.
4. The top three arrival airports.
5. Domestic versus international routes.
6. The five latest scheduled arrivals at DEL.
7. Airports with no recorded arrivals.
8. Flight counts by airline and status.
9. Canceled flights.
10. Routes flown by more than two aircraft models.
11. Delayed-flight percentage by destination.

## 6. Dashboard

The Streamlit dashboard displays airport and flight totals, flights by aircraft model, flight counts by airline and status, domestic/international route counts, delayed-flight percentages, airport summaries, and flight reports.

The dashboard combines static airport reference information with a temporary flight snapshot. Counts in aircraft-specific views depend on the records that include aircraft details. Dashboard screenshots are kept outside this repository.

## 7. Interpretation and limitations

- Flight records retrieved from the API are temporary snapshots, not historical data collected over a long period.
- Many routes were excluded because the opposite airport was not in the selected 15-airport reference list.
- Some API records did not contain enough information to normalize and were skipped.
- Live updates are subject to AeroDataBox coverage; some airports may provide scheduled information only.
- A delayed-flight percentage from a small, short-term sample should not be presented as an airport's usual delay rate.
- API content must be attributed and deleted within the applicable free-plan retention period. See the [AeroDataBox terms](https://aerodatabox.com/terms).

## 8. Conclusion

The project demonstrates a beginner workflow from relational storage and SQL analysis to a working dashboard. Flight-data availability and coverage depend on the temporary API snapshot and selected airport list.

