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

        # Skyscanner Redirect Link Generation
        # Try to clean strings for URL (lowercase, hyphens)
        def clean_for_url(s):
            return s.lower().replace(" ", "-").replace(",", "")

        src_slug = clean_for_url(req.source)
        dest_slug = clean_for_url(req.destination)
        
        # Skyscanner format: /transport/flights/{origin}/{destination}/{yymmdd}/{yymmdd}
        # Dates needed in YYMMDD
        try:
            from datetime import datetime as dt
            s_date = dt.strptime(req.start_date, "%Y-%m-%d").strftime("%y%m%d")
            e_date = dt.strptime(req.end_date, "%Y-%m-%d").strftime("%y%m%d")
            
            # Simple deep link attempt using slugs - Skyscanner is smart enough to handle city names often
            # or fallback to search.
            skyscanner_link = f"https://www.skyscanner.co.in/transport/flights/{src_slug}/{dest_slug}/{s_date}/{e_date}"
        except:
            skyscanner_link = "https://www.skyscanner.co.in/"

        # Calculate actual number of days for the prompt
        from datetime import datetime as dt
        start = dt.strptime(req.start_date, "%Y-%m-%d")
        end = dt.strptime(req.end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1  # Include both start and end dates

        # Dummy flight object for frontend to render the button
        flight_data = [{
            "airline": "Skyscanner Search",
            "flight_number": "SKY-LINK",
            "departure_time": "",
            "arrival_time": "",
            "duration": "",
            "price": "Check Prices",
            "booking_link": skyscanner_link
        }]

        prompt = (
            f"Create a detailed, deep-dive {num_days}-day trip plan for {req.destination} "
            f"for {req.travelers} traveler(s), from {req.start_date} to {req.end_date}. "
            f"Budget: ₹{req.budget_inr or 'flexible'}. "
            f"Preferences: {', '.join(req.preferences or [])}. "
            f"\n\n"
            f"Please structure your response STRICTLY as follows:\n"
            f"1. **Accommodations**: Suggest 3 specific, highly-rated hotels/resorts with estimated prices per night.\n"
            f"2. **Detailed Itinerary**: A COMPLETE, IMMERSIVE day-by-day itinerary for ALL {num_days} days. "
            f"For each day, use format '### Day X - [Date]' (e.g., ### Day 1 - {req.start_date}). "
            f"Provide specific timings (Morning, Afternoon, Evening) with deep explanations of *why* to visit each spot, history, or vibe. "
            f"Make it feel like a professional travel guide.\n"
            f"3. **Budget Breakdown**: A table summarizing costs STRICTLY for: Hotels, Food, Activities, and Local Transport. "
            f"❌ DO NOT INCLUDE FLIGHT COSTS in this table.\n\n"
            f"**Tone & Formatting**: \n"
            f"- Use **Header 1 (#)** for main title, **Header 2 (##)** for sections like Itinerary/Budget.\n"
            f"- Use **Bold** for key places and times.\n"
            f"- Use emojis ✨🌊🍛 *generously* to make it visually engaging and fun.\n"
            f"- Use varied font sizes (headers) to organize information clearly."
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
