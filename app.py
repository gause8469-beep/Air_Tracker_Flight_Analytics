import mysql.connector
import pandas as pd
import streamlit as st

from src.db_connection import get_connection


st.set_page_config(page_title="Air Tracker Analytics", page_icon="✈️", layout="wide")
st.title("✈️ Air Tracker Flight Analytics")
st.caption(
    "Flight data source: [AeroDataBox](https://aerodatabox.com/). "
    "API flight records are a temporary snapshot and must be removed within 7 days."
)


def load_dashboard_data():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS airport_count FROM airport")
        airport_count = cursor.fetchone()["airport_count"]

        cursor.execute("SELECT COUNT(*) AS flight_count FROM flights")
        flight_count = cursor.fetchone()["flight_count"]

        cursor.execute(
            """
            SELECT iata_code, name, city, country
            FROM airport
            ORDER BY country, city
            """
        )
        airports = cursor.fetchall()

        cursor.execute(
            """
            SELECT aircraft.model, COUNT(flights.flight_id) AS total_flights
            FROM flights
            JOIN aircraft
                ON flights.aircraft_registration = aircraft.registration
            GROUP BY aircraft.model
            ORDER BY total_flights DESC
            """
        )
        flights_by_model = cursor.fetchall()

        cursor.execute(
            """
            SELECT aircraft.registration, aircraft.model,
                   COUNT(flights.flight_id) AS total_flights
            FROM aircraft
            JOIN flights
                ON flights.aircraft_registration = aircraft.registration
            GROUP BY aircraft.registration, aircraft.model
            HAVING COUNT(flights.flight_id) > 5
            ORDER BY total_flights DESC
            """
        )
        frequent_aircraft = cursor.fetchall()

        cursor.execute(
            """
            SELECT airport.iata_code, airport.name,
                   COUNT(flights.flight_id) AS departing_flights
            FROM airport
            JOIN flights
                ON flights.origin_iata = airport.iata_code
            GROUP BY airport.iata_code, airport.name
            HAVING COUNT(flights.flight_id) > 5
            ORDER BY departing_flights DESC
            """
        )
        busy_departure_airports = cursor.fetchall()

        cursor.execute(
            """
            SELECT airport.iata_code, airport.name,
                   COUNT(flights.flight_id) AS arriving_flights
            FROM airport
            JOIN flights
                ON flights.destination_iata = airport.iata_code
            GROUP BY airport.iata_code, airport.name
            ORDER BY arriving_flights DESC
            LIMIT 3
            """
        )
        top_arrival_airports = cursor.fetchall()

        cursor.execute(
            """
            SELECT airline_code, status, COUNT(*) AS flight_count
            FROM flights
            GROUP BY airline_code, status
            ORDER BY airline_code, status
            """
        )
        flights_by_airline_status = cursor.fetchall()

        cursor.execute(
            """
            SELECT destination_iata,
                   COUNT(*) AS total_flights,
                   SUM(CASE WHEN LOWER(status) = 'delayed' THEN 1 ELSE 0 END)
                       AS delayed_flights,
                   ROUND(
                       100.0 * SUM(CASE WHEN LOWER(status) = 'delayed' THEN 1 ELSE 0 END)
                       / COUNT(*),
                       2
                   ) AS delayed_percentage
            FROM flights
            GROUP BY destination_iata
            ORDER BY delayed_percentage DESC
            """
        )
        delay_by_destination = cursor.fetchall()

        cursor.execute(
            """
            SELECT flight_type, COUNT(*) AS flight_count
            FROM (
                SELECT CASE
                    WHEN origin.country IS NULL OR destination.country IS NULL
                        THEN 'Unknown'
                    WHEN origin.country = destination.country THEN 'Domestic'
                    ELSE 'International'
                END AS flight_type
                FROM flights
                JOIN airport AS origin
                    ON flights.origin_iata = origin.iata_code
                JOIN airport AS destination
                    ON flights.destination_iata = destination.iata_code
            ) AS classified_flights
            GROUP BY flight_type
            ORDER BY flight_type
            """
        )
        flight_types = cursor.fetchall()

        cursor.execute(
            """
            SELECT flight_id, flight_number, airline_code,
                   origin_iata, destination_iata, status
            FROM flights
            WHERE LOWER(status) IN ('canceled', 'cancelled')
            ORDER BY flight_id
            """
        )
        canceled_flights = cursor.fetchall()

        cursor.execute(
            """
            SELECT airport.iata_code, airport.name
            FROM airport
            LEFT JOIN flights
                ON flights.destination_iata = airport.iata_code
            WHERE flights.flight_id IS NULL
            ORDER BY airport.iata_code
            """
        )
        airports_without_arrivals = cursor.fetchall()

        cursor.execute(
            """
            SELECT origin.city AS origin_city,
                   destination.city AS destination_city,
                   COUNT(DISTINCT aircraft.model) AS different_models
            FROM flights
            JOIN airport AS origin
                ON flights.origin_iata = origin.iata_code
            JOIN airport AS destination
                ON flights.destination_iata = destination.iata_code
            JOIN aircraft
                ON flights.aircraft_registration = aircraft.registration
            GROUP BY origin.city, destination.city
            HAVING COUNT(DISTINCT aircraft.model) > 2
            ORDER BY different_models DESC
            """
        )
        routes_by_model = cursor.fetchall()

        cursor.execute(
            """
            SELECT flight_id, flight_number, airline_code, origin_iata,
                   scheduled_arrival, status
            FROM flights
            WHERE destination_iata = 'DEL'
            ORDER BY scheduled_arrival DESC
            LIMIT 5
            """
        )
        delhi_arrivals = cursor.fetchall()

        return {
            "airport_count": airport_count,
            "flight_count": flight_count,
            "airports": airports,
            "flights_by_model": flights_by_model,
            "frequent_aircraft": frequent_aircraft,
            "busy_departure_airports": busy_departure_airports,
            "top_arrival_airports": top_arrival_airports,
            "flights_by_airline_status": flights_by_airline_status,
            "delay_by_destination": delay_by_destination,
            "flight_types": flight_types,
            "canceled_flights": canceled_flights,
            "airports_without_arrivals": airports_without_arrivals,
            "routes_by_model": routes_by_model,
            "delhi_arrivals": delhi_arrivals,
        }
    finally:
        cursor.close()
        connection.close()


try:
    dashboard_data = load_dashboard_data()
    airport_count = dashboard_data["airport_count"]
    flight_count = dashboard_data["flight_count"]

    first_metric, second_metric = st.columns(2)
    first_metric.metric("Airports", airport_count)
    second_metric.metric("Flights", flight_count)

    st.subheader("Flight analytics")
    if flight_count == 0:
        st.info(
            "No flight records are in the database yet. The charts and flight reports "
            "will populate after real flight data is added."
        )
    else:
        flights_tab, routes_tab, reports_tab = st.tabs(
            ["Flight counts", "Routes and airports", "Flight reports"]
        )

        with flights_tab:
            model_data = pd.DataFrame(dashboard_data["flights_by_model"])
            status_data = pd.DataFrame(dashboard_data["flights_by_airline_status"])

            left_chart, right_chart = st.columns(2)
            with left_chart:
                st.markdown("**Flights by aircraft model**")
                if model_data.empty:
                    st.info("No aircraft model data is available yet.")
                else:
                    st.bar_chart(model_data, x="model", y="total_flights")

            with right_chart:
                st.markdown("**Flights by airline and status**")
                if status_data.empty:
                    st.info("No airline status data is available yet.")
                else:
                    st.dataframe(status_data, hide_index=True, width="stretch")

            st.markdown("**Aircraft appearing on more than five flights**")
            if dashboard_data["frequent_aircraft"]:
                st.dataframe(
                    pd.DataFrame(dashboard_data["frequent_aircraft"]),
                    hide_index=True,
                    width="stretch",
                )
            else:
                st.info(
                    "No aircraft appears on more than five flights in this snapshot."
                )

        with routes_tab:
            type_data = pd.DataFrame(dashboard_data["flight_types"])
            delay_data = pd.DataFrame(dashboard_data["delay_by_destination"])
            if not delay_data.empty:
                delay_data["delayed_percentage"] = pd.to_numeric(
                    delay_data["delayed_percentage"], errors="coerce"
                ).astype("float64")

            left_chart, right_chart = st.columns(2)
            with left_chart:
                st.markdown("**Domestic and international flights**")
                if type_data.empty:
                    st.info("No route classification data is available yet.")
                else:
                    st.bar_chart(type_data, x="flight_type", y="flight_count")

            with right_chart:
                st.markdown("**Delayed-flight percentage by destination**")
                if delay_data.empty:
                    st.info("No delay data is available yet.")
                else:
                    st.bar_chart(
                        delay_data,
                        x="destination_iata",
                        y="delayed_percentage",
                    )

            busiest, arrivals = st.columns(2)
            with busiest:
                st.markdown("**Airports with more than five departures**")
                st.dataframe(
                    pd.DataFrame(dashboard_data["busy_departure_airports"]),
                    hide_index=True,
                    width="stretch",
                )
            with arrivals:
                st.markdown("**Top three arrival airports**")
                st.dataframe(
                    pd.DataFrame(dashboard_data["top_arrival_airports"]),
                    hide_index=True,
                    width="stretch",
                )

            st.markdown("**Routes flown by more than two aircraft models**")
            st.dataframe(
                pd.DataFrame(dashboard_data["routes_by_model"]),
                hide_index=True,
                width="stretch",
            )

        with reports_tab:
            st.markdown("**Five latest scheduled arrivals at DEL**")
            st.dataframe(
                pd.DataFrame(dashboard_data["delhi_arrivals"]),
                hide_index=True,
                width="stretch",
            )

            st.markdown("**Canceled flights**")
            st.dataframe(
                pd.DataFrame(dashboard_data["canceled_flights"]),
                hide_index=True,
                width="stretch",
            )

            st.markdown("**Airports with no recorded arrivals**")
            st.dataframe(
                pd.DataFrame(dashboard_data["airports_without_arrivals"]),
                hide_index=True,
                width="stretch",
            )

    st.subheader("Airport reference list")
    st.dataframe(
        pd.DataFrame(dashboard_data["airports"]),
        hide_index=True,
        width="stretch",
    )
except mysql.connector.Error as error:
    st.error(f"Could not connect to the MySQL database: {error}")
