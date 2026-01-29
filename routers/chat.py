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
    print(f"DEBUG: Received chat request from user {current_user.email}")
    
    # 1. Save User Message
    try:
        user_msg = models.ChatMessage(
            user_id=current_user.id,
            role="user",
            content=req.message
        )
        db.add(user_msg)
        db.commit()
        print("DEBUG: Saved user message to database")
    except Exception as e:
        print(f"DATABASE ERROR (User Message): {e}")
        # Even if DB fails, we should try to get helpful AI response back if possible
        # but for a production app, we usually want persistence.
        # Let's keep going but log it.

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "TripMate AI",
    }
    
    messages_payload = [{"role": "system", "content": "You are a helpful AI travel planner. Please be professional. Use emojis ONLY for bullet points or lists, and very sparingly in paragraphs. Do not overuse them."}]
    
    try:
        recent_history = db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == current_user.id
        ).order_by(models.ChatMessage.timestamp.desc()).limit(6).all()
        # Reverse to chrono order
        recent_history = recent_history[::-1]
        
        for msg in recent_history:
            messages_payload.append({"role": msg.role, "content": msg.content})
        print(f"DEBUG: Prepared payload with {len(messages_payload)} messages")
    except Exception as e:
        print(f"DATABASE ERROR (History Fetch): {e}")
        messages_payload.append({"role": "user", "content": req.message})
        
    payload = {
        "model": model,
        "messages": messages_payload,
    }

    try:
        print(f"DEBUG: Calling OpenRouter API with model {model}")
        # Using a timeout to prevent hanging
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            error_detail = response.text
            print(f"OPENROUTER API ERROR: Status {response.status_code}, Body: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=f"OpenRouter Error: {error_detail}")

        data = response.json()
        if "choices" not in data or not data["choices"]:
             print(f"OPENROUTER INVALID RESPONSE: {data}")
             raise HTTPException(status_code=502, detail="Invalid response from AI provider")
             
        bot_reply = data["choices"][0]["message"]["content"]
        print("DEBUG: Received AI reply")
        
        # 2. Save Bot Response
        try:
            bot_msg = models.ChatMessage(
                user_id=current_user.id,
                role="assistant",
                content=bot_reply
            )
            db.add(bot_msg)
            db.commit()
            print("DEBUG: Saved bot response to database")
        except Exception as e:
            print(f"DATABASE ERROR (Bot Message): {e}")
        
        return {"reply": bot_reply}
        
    except requests.exceptions.Timeout:
        print("OPENROUTER TIMEOUT")
        raise HTTPException(status_code=504, detail="AI Assistant timed out. Please try again.")
    except Exception as e:
        print(f"CHAT UNEXPECTED ERROR: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
