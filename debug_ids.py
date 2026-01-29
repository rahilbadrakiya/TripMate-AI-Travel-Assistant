import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def debug_ids(query):
    headers = {
        "x-rapidapi-host": "sky-scrapper.p.rapidapi.com",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY")
    }
    url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport"
    params = {"query": query, "locale": "en-US"}
    
    print(f"Searching for '{query}'...")
    req = requests.get(url, headers=headers, params=params)
    if req.status_code == 200:
        data = req.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {req.text}")

if __name__ == "__main__":
    debug_ids("Mumbai")
    debug_ids("Dubai")
    debug_ids("Phuket") # User's query
