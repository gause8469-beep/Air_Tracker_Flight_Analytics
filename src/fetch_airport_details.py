from api_client import get_json


def fetch_airport_details(iata_code):
    """Return details for one airport. Calling this function sends an API request."""
    code = iata_code.strip().upper()

    if len(code) != 3 or not code.isalpha():
        raise ValueError("Enter a three-letter IATA airport code.")

    return get_json(f"airports/iata/{code}")

