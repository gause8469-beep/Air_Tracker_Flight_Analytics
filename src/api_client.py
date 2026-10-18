import os
from pathlib import Path

import requests
from dotenv import load_dotenv


project_folder = Path(__file__).resolve().parent.parent
load_dotenv(project_folder / ".env")

api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST")


def get_json(endpoint, params=None):
    """Send one request and return the response as JSON."""
    if not api_key or not api_host:
        raise ValueError("Check RAPIDAPI_KEY and RAPIDAPI_HOST in .env.")

    url = f"https://{api_host}/{endpoint.lstrip('/')}"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    if response.status_code == 429:
        raise RuntimeError("API limit reached. Stop and check the quota.")

    response.raise_for_status()
    if response.status_code == 204 or not response.content:
        return None
    return response.json()

