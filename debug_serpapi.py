from serpapi import GoogleSearch
import os
from dotenv import load_dotenv
import json

load_dotenv()

def debug_serp():
    key = os.getenv("SERPAPI_API_KEY")
    if not key:
        print("No SERPAPI_API_KEY found.")
        return

    print(f"Using Key: {key[:5]}...")
    
    params = {
        "engine": "google_flights",
        "departure_id": "BOM",
        "arrival_id": "DXB",
        "outbound_date": "2026-02-06", # Future date
        "currency": "INR",
        "hl": "en",
        "api_key": key,
        "type": "2" 
    }

    try:
        print("Fetching from SerpApi...")
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for errors
        if "error" in results:
            print(f"API Error: {results['error']}")
            return

        # Dump raw first result
        flights_list = results.get("best_flights", []) + results.get("other_flights", [])
        print(f"Found {len(flights_list)} flights.")
        
        if flights_list:
            first = flights_list[0]
            print("\n--- Raw First Flight Data ---")
            print(json.dumps(first, indent=2))
            
            # Simulate parsing
            print("\n--- Parsed Data check ---")
            flight_leg = first.get("flights", [{}])[0]
            airline = flight_leg.get("airline", "Unknown")
            flight_no = flight_leg.get("flight_number", "")
            price = first.get("price", 0)
            duration = first.get("total_duration")
            
            print(f"Airline: {airline}")
            print(f"Flight No: {flight_no}")
            print(f"Price: {price}")
            print(f"Duration: {duration}")
            
        else:
            print("No flights found in 'best_flights' or 'other_flights'.")
            print("Keys available:", results.keys())

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_serp()
