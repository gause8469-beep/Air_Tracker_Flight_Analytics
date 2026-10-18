import os
from pathlib import Path

from dotenv import load_dotenv


project_folder = Path(__file__).resolve().parent.parent
env_file = project_folder / ".env"

load_dotenv(env_file)

api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST")

print("API key found:", "yes" if api_key else "no")
print(
    "API host correct:",
    "yes" if api_host == "aerodatabox.p.rapidapi.com" else "no",
)

