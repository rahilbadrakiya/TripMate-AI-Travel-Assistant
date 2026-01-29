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

@router.post("/chat")
async def chat_with_bot(req: ChatRequest):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "TripMate AI",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI travel planner."},
            {"role": "user", "content": req.message},
        ],
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Chat error: {response.text}")

    data = response.json()
    return {"reply": data["choices"][0]["message"]["content"]}
