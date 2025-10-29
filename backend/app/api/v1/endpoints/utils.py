from fastapi import APIRouter, status
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "PrepMind API is running"
    }


@router.post("/feedback", response_model=ResponseBase)
async def submit_feedback():
    """Submit user feedback"""
    return ResponseBase(
        success=True,
        message="Feedback submitted successfully"
    )
