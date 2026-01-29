from fastapi import APIRouter
from models import RecommendRequest, RecommendResponse

router = APIRouter(prefix="/recommend", tags=["Recommend"])

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
