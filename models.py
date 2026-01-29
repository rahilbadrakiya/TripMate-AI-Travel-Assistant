from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True) # Default to True now
    verification_token = Column(String, nullable=True) # Simple token for MVP

    trips = relationship("Trip", back_populates="owner")
    messages = relationship("ChatMessage", back_populates="user")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String) # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="messages")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, index=True) # Using String ID from frontend (timestamp)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    destination = Column(String, index=True)
    start_date = Column(String)
    end_date = Column(String)
    travelers = Column(Integer)
    budget_inr = Column(Float, nullable=True)
    
    itinerary_markdown = Column(Text)
    flights_data = Column(JSON, nullable=True) # Store list of flights (JSON)
    image_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="trips")
