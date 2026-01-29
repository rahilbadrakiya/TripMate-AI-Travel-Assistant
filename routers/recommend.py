from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/recommend", tags=["Recommend"])

class RecommendRequest(BaseModel):
    destination: str

class RecommendResponse(BaseModel):
    recommendations: List[str]

@router.post("", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    base = [
        "Top budget-friendly stays",
        "Famous local restaurants",
        "Hidden-viewpoint sunrise spots",
        "Best evening markets",
        "Photogenic places for reels"
    ]
    return RecommendResponse(recommendations=base)
