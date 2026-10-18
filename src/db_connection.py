import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# Find the project folder and read its .env settings.
project_folder = Path(__file__).resolve().parent.parent
load_dotenv(project_folder / ".env")


def get_connection():
    """Connect to the project's MySQL database and return the connection."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )


# Run a quick connection check when this file is run directly.
if __name__ == "__main__":
    connection = None

    try:
        connection = get_connection()
        print("Database connection successful.")
        print(f"Connected to: {connection.database}")

    except mysql.connector.Error as error:
        print(f"Could not connect to the database: {error}")

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("Connection closed.")

