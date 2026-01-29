from pydantic import BaseModel, Field
from typing import List, Optional

# ===== PLAN =====
class PlanRequest(BaseModel):
    destination: str = Field(..., min_length=2)
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    travelers: int = 1
    budget_inr: Optional[float] = None
    preferences: Optional[List[str]] = None  # e.g. ["beaches","food","adventure"]

class Hotel(BaseModel):
    name: str
    area: str
    price_per_night_inr: float
    link: str

class PlanResponse(BaseModel):
    itinerary_markdown: str
    hotels: List[Hotel]
    weather_summary: str
    cost_summary_markdown: str

# ===== CHAT =====
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str

# ===== RECOMMEND =====
class RecommendRequest(BaseModel):
    destination: str
    days: int
    budget_inr: Optional[float] = None

class RecommendResponse(BaseModel):
    recommendations: List[str]
