from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    name: str

class User(UserBase):
    id: int
    is_active: bool
    name: str | None = None
    username: str | None = None

    class Config:
        from_attributes = True

# --- Trip Schemas ---
# Matches Flutter TripPlan logic

class Flight(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration: str
    price: str
    booking_link: str

class TripBase(BaseModel):
    id: str
    destination: str
    start_date: str
    end_date: str
    travelers: int
    budget_inr: Optional[float] = None
    itinerary_markdown: str
    flights: Optional[List[Flight]] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

class TripCreate(TripBase):
    pass

class Trip(TripBase):
    user_id: int 

    class Config:
        from_attributes = True
