import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("MODEL", "meta-llama/llama-3.1-8b-instruct")

if not api_key:
    raise ValueError("Missing OPENROUTER_API_KEY in .env file")

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

class ChatRequest(BaseModel):
    message: str

from datetime import datetime
import crud, models, database
from .auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import Depends

@router.get("/history")
async def get_chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # Fetch last 50 messages
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.timestamp.desc()).limit(50).all()
    
    # Return in chronological order
    return [
        {
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in messages[::-1]
    ]

@router.post("/chat")
async def chat_with_bot(
    req: ChatRequest, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Save User Message
    user_msg = models.ChatMessage(
        user_id=current_user.id,
        role="user",
        content=req.message
    )
    db.add(user_msg)
    db.commit()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "TripMate AI",
    }
    
    # Context improvement: fetch last few messages to maintain conversation flow?
    # For now, keeping it simple as per request, just chat. 
    # But for "continue chat", maybe I should send context? 
    # The user asked: "after re lunching application user can chat into last chat continue"
    # This implies context window. I will fetch last 5 messages as context.
    
    recent_history = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.timestamp.desc()).limit(6).all()
    # Reverse to chrono order
    recent_history = recent_history[::-1] # these includes the one we just saved? yes.
    
    messages_payload = [{"role": "system", "content": "You are a helpful AI travel planner. Please be professional. Use emojis ONLY for bullet points or lists, and very sparingly in paragraphs. Do not overuse them."}]
    
    for msg in recent_history:
        messages_payload.append({"role": msg.role, "content": msg.content})
        
    # If the just saved one is not in recent_history (unlikely unless limit is small), it's fine.
    # Actually, recent_history includes the one we just added because we committed it.
    
    payload = {
        "model": model,
        "messages": messages_payload,
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Chat error: {response.text}")

        data = response.json()
        bot_reply = data["choices"][0]["message"]["content"]
        
        # 2. Save Bot Response
        bot_msg = models.ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=bot_reply
        )
        db.add(bot_msg)
        db.commit()
        
        return {"reply": bot_reply}
        
    except Exception as e:
        print(f"Chat Error: {e}")
        # If external API fails, we might want to delete the user message or just leave it?
        # Leaving it is fine, it's a failed attempt.
        raise HTTPException(status_code=500, detail=str(e))
