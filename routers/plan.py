import os
import requests
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# ✅ Use OpenRouter instead of OpenAI
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

MODEL = os.getenv("MODEL", "meta-llama/llama-3.3-70b-instruct")

class PlanRequest(BaseModel):
    source: str
    destination: str
    start_date: str
    end_date: str
    travelers: int
    budget_inr: float | None = None
    preferences: list[str] | None = None

def fetch_destination_image(destination: str) -> str | None:
    try:
        # Search for the page title first
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": destination,
            "srlimit": 1
        }
        headers = {
            "User-Agent": "TripMate/1.0 (contact@example.com)"
        }
        
        response = httpx.get(search_url, params=search_params, headers=headers, timeout=5.0)
        
        if response.status_code != 200:
            print(f"Wikipedia Search Error: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        
        if not data.get("query", {}).get("search"):
            return None
            
        page_title = data["query"]["search"][0]["title"]
        
        # Get the page summary/image
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
        response = httpx.get(summary_url, headers=headers, timeout=5.0)
        
        if response.status_code == 200:
            summary_data = response.json()
            return summary_data.get("thumbnail", {}).get("source")
        else:
             print(f"Wikipedia Summary Error: {response.status_code} - {response.text}")
             return None
            
    except Exception as e:
        print(f"Error fetching image for {destination}: {e}")
        return None

from serpapi import GoogleSearch
import os
import random
from datetime import datetime, timedelta

def get_sky_ids(query: str, headers: dict) -> tuple[str, str] | None:
    # This helper is no longer needed for SerpApi but kept to minimize diff noise or can be removed.
    # For cleanliness, I will allow the tool to just replace the whole function block.
    pass 

def fetch_real_flights(source: str, destination: str, start_date: str, end_date: str) -> list[dict]:
    """
    Fetches exactly TWO 'Best' flights:
    1. Best Outbound (Source -> Dest) on Start Date
    2. Best Return (Dest -> Source) on End Date
    Uses SerpApi (Google Flights). Falls back to Mock if failed.
    """
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    flight_results = []
    
    # Helper to fetch one leg
    def fetch_leg(origin, dest, date, label):
        if not serpapi_key: return None
        try:
            print(f"Fetching {label} flight: {origin} -> {dest} on {date}")
            params = {
                "engine": "google_flights",
                "departure_id": origin,
                "arrival_id": dest,
                "outbound_date": date, 
                "currency": "INR",
                "hl": "en",
                "api_key": serpapi_key,
                "type": "2" # One-way search for this leg
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Get the single Best match
            flights_list = results.get("best_flights", []) or results.get("other_flights", [])
            if not flights_list: return None
            
            best_flight = flights_list[0]
            
            # Parse
            flight_leg = best_flight.get("flights", [{}])[0]
            airline = flight_leg.get("airline", "Unknown Airline")
            flight_no = flight_leg.get("flight_number", "")
            
            dep_time = flight_leg.get("departure_airport", {}).get("time", "")
            arr_time = flight_leg.get("arrival_airport", {}).get("time", "")
            
            duration = (best_flight.get("total_duration") or "0") + " min"
            price = best_flight.get("price", 0)
            
            # Specific booking link
            query = f"flights from {origin} to {dest} on {date} {airline}"
            booking_link = f"https://www.google.com/travel/flights?q={query.replace(' ', '+')}"
            
            return {
                "airline": f"{label}: {airline}", # Label it "Going" or "Return"
                "flight_number": flight_no,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "duration": f"{int(duration.split(' ')[0]) // 60}h {int(duration.split(' ')[0]) % 60}m",
                "price": f"₹{price}",
                "booking_link": booking_link
            }
        except Exception as e:
            print(f"Error fetching {label}: {e}")
            return None

    # 1. Fetch Outbound
    outbound = fetch_leg(source, destination, start_date, "Going")
    if outbound: flight_results.append(outbound)
    
    # 2. Fetch Return
    inbound = fetch_leg(destination, source, end_date, "Return")
    if inbound: flight_results.append(inbound)

    # Return if we found both/any
    if flight_results:
        return flight_results
        
    # --- MOCK FALLBACK ---
    print("Using Mock Flight Data (Fallback)")
    mock_flights = []
    
    # Mock Outbound
    base_mins = 120 + random.randint(0, 100)
    dep_dt = datetime.strptime(f"{random.randint(6, 20)}:00", "%H:%M")
    arr_dt = dep_dt + timedelta(minutes=base_mins)
    mock_flights.append({
        "airline": "Going: IndiGo (Best)",
        "flight_number": "6E-501",
        "departure_time": dep_dt.strftime("%H:%M"),
        "arrival_time": arr_dt.strftime("%H:%M"),
        "duration": f"{base_mins//60}h {base_mins%60}m",
        "price": f"₹{random.randint(4000, 8000):,}",
        "booking_link": f"https://www.google.com/travel/flights?q=flights+from+{source}+to+{destination}+on+{start_date}+IndiGo"
    })
    
    # Mock Return
    dep_dt_ret = datetime.strptime(f"{random.randint(6, 20)}:00", "%H:%M")
    arr_dt_ret = dep_dt_ret + timedelta(minutes=base_mins)
    mock_flights.append({
        "airline": "Return: Air India (Best)",
        "flight_number": "AI-804",
        "departure_time": dep_dt_ret.strftime("%H:%M"),
        "arrival_time": arr_dt_ret.strftime("%H:%M"),
        "duration": f"{base_mins//60}h {base_mins%60}m",
        "price": f"₹{random.randint(4000, 8000):,}",
        "booking_link": f"https://www.google.com/travel/flights?q=flights+from+{destination}+to+{source}+on+{end_date}+Air+India"
    })
    
    return mock_flights

@router.post("/plan")
def plan_trip(req: PlanRequest):
    try:
        # Fetch image
        image_url = fetch_destination_image(req.destination)

        # Fetch real flights (Parallelizable in production)
        # Now returns a list of dictionaries (JSON) instead of a string
        flight_data = fetch_real_flights(req.source, req.destination, req.start_date, req.end_date)

        # Create a natural-language prompt for the itinerary
        # Calculate actual number of days
        from datetime import datetime as dt
        start = dt.strptime(req.start_date, "%Y-%m-%d")
        end = dt.strptime(req.end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1  # Include both start and end dates
        
        prompt = (
            f"Create a detailed {num_days}-day trip plan for {req.destination} "
            f"for {req.travelers} traveler(s), from {req.start_date} to {req.end_date}. "
            f"Budget: ₹{req.budget_inr or 'flexible'}. "
            f"Preferences: {', '.join(req.preferences or [])}. "
            f"\n\nHere are the flight options found:\n{flight_data}\n\n"
            f"Please structure your response STRICTLY as follows:\n"
            f"1. **Flights**: Briefly summarize the best flight options from the data provided above.\n"
            f"2. **Hotels**: Suggest 3 good hotel options with estimated prices.\n"
            f"3. **Itinerary**: A COMPLETE day-by-day itinerary for ALL {num_days} days. "
            f"IMPORTANT: You MUST include EVERY day from Day 1 to Day {num_days}. "
            f"For each day, use format '### Day X - [Date]' (e.g., ### Day 1 - {req.start_date}), "
            f"then list Morning, Afternoon, and Evening activities with timings and descriptions. "
            f"Do NOT skip or combine any days. Each day must have its own section.\n"
            f"4. **Budget Breakdown**: A table summarizing costs (Flights, Hotels, Food, Activities, Total).\n\n"
            f"Tone: Professional and helpful. Use emojis VERY sparingly (max 1 per section header). Do not clutter text with emojis. Keep it clean and informative."
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json",
        }

        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        itinerary_body = response.json()["choices"][0]["message"]["content"]
        
        return {
            "itinerary_markdown": itinerary_body,
            "flights": flight_data,
            "image_url": image_url
        }

    except Exception as e:
        print(f"Plan Trip Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
