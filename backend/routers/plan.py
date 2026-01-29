import os
import requests
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
    destination: str
    start_date: str
    end_date: str
    travelers: int
    budget_inr: float | None = None
    preferences: list[str] | None = None


@router.post("/plan")
def plan_trip(req: PlanRequest):
    try:
        # Create a natural-language prompt
        prompt = (
            f"Create a detailed {req.travelers}-day trip plan for {req.destination} "
            f"from {req.start_date} to {req.end_date}. "
            f"Budget: ₹{req.budget_inr or 'flexible'}. "
            f"Preferences: {', '.join(req.preferences or [])}. "
            f"Include day-wise itinerary, hotel suggestions, and weather overview."
        )

        # Send request to OpenRouter
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

        reply = response.json()["choices"][0]["message"]["content"]
        return {"itinerary_markdown": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
