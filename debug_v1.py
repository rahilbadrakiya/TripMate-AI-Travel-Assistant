import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def debug_v1():
    key = os.getenv("RAPIDAPI_KEY")
    if not key:
        print("No RAPIDAPI_KEY found.")
        return

    headers = {
        "x-rapidapi-host": "sky-scrapper.p.rapidapi.com",
        "x-rapidapi-key": key
    }
    
    # 1. Search Airport (V1)
    print("--- 1. Testing V1 searchAirport ---")
    url_search = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport"
    params_search = {"query": "New York", "locale": "en-US"}
    
    try:
        res = requests.get(url_search, headers=headers, params=params_search)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            # print(json.dumps(data, indent=2))
            if data.get("status") and data.get("data"):
                first = data["data"][0]
                origin_sky = first.get("skyId")
                origin_entity = first.get("entityId")
                print(f"Found Origin: {origin_sky} ({origin_entity})")
                
                # Setup proper destination for test (e.g. London)
                dest_sky = "LOND"
                dest_entity = "27544008" # Approximate, hardcoded for test
                
                # 2. Search Flights (V1)
                print("\n--- 2. Testing V1 searchFlights ---")
                url_flight = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchFlights"
                params_flight = {
                    "originSkyId": origin_sky,
                    "destinationSkyId": dest_sky,
                    "originEntityId": origin_entity,
                    "destinationEntityId": dest_entity,
                    "date": "2025-03-01",
                    "cabinClass": "economy",
                    "adults": "1",
                    "sortBy": "best",
                    "currency": "USD",
                    "market": "en-US",
                    "countryCode": "US"
                }
                
                print(f"Requesting flights: {params_flight}")
                res_flight = requests.get(url_flight, headers=headers, params=params_flight)
                print(f"Flight Status: {res_flight.status_code}")
                if res_flight.status_code == 200:
                    f_data = res_flight.json()
                    print("Flight Data Keys:", f_data.keys())
                    if "data" in f_data:
                        print("Data keys:", f_data["data"].keys())
                        # Check specific structure
                        itineraries = f_data["data"].get("itineraries", [])
                        print(f"Itineraries found: {len(itineraries)}")
                else:
                    print(res_flight.text)
            else:
                print("No airport data found.")
        else:
            print(res.text)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_v1()
