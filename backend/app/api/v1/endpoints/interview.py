from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interview import Interview, InterviewResult
from app.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewListItem,
    InterviewResultResponse
)
from app.schemas.common import ResponseBase, PaginatedResponse
from app.services.interview_service import InterviewService
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()


@router.post("/create", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new interview with AI-generated questions.
    
    Steps:
    1. Validate input (interview type, technologies, difficulty)
    2. Use AI (Gemini) to generate relevant questions
    3. Save interview to database with status='draft'
    4. Return interview with questions
    
    The interview can then be started via WebSocket endpoint.
    """
    interview = InterviewService.create_interview(db, current_user.id, interview_data)
    return interview


@router.get("/list", response_model=List[InterviewListItem])
async def list_interviews(
    status: Optional[str] = Query(None, regex="^(draft|in_progress|completed|abandoned)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all interviews for the current user.
    
    Optional filter by status:
    - draft: Interview created but not started
    - in_progress: Interview currently active
    - completed: Interview finished
    - abandoned: Interview started but not completed
    """
    interviews = InterviewService.get_user_interviews(db, current_user.id, status)
    return interviews


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific interview including questions.
    
    Use this to preview questions before starting the interview.
    """
    interview = InterviewService.get_interview(db, interview_id, current_user.id)
    return interview


@router.delete("/{interview_id}", response_model=ResponseBase)
async def delete_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an interview.
    
    Can only delete interviews with status='draft'.
    Completed interviews cannot be deleted to maintain records.
    """
    InterviewService.delete_interview(db, interview_id, current_user.id)
    return ResponseBase(
        success=True,
        message="Interview deleted successfully"
    )


@router.post("/{interview_id}/regenerate-questions", response_model=InterviewResponse)
async def regenerate_questions(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate questions for a draft interview.
    
    Useful if the user is not satisfied with the generated questions.
    Can only regenerate for interviews with status='draft'.
    """
    interview = InterviewService.get_interview(db, interview_id, current_user.id)
    
    if interview.status != "draft":
        raise BadRequestException("Can only regenerate questions for draft interviews")
    
    # Generate new questions
    new_questions = InterviewService.generate_questions(
        interview_type=interview.interview_type,
        target_role=interview.target_role,
        technologies=interview.technologies,
        difficulty=interview.difficulty,
        num_questions=interview.num_questions
    )
    
    # Update interview
    interview.questions = new_questions
    db.commit()
    db.refresh(interview)
    
    return interview


@router.get("/{interview_id}/result", response_model=InterviewResultResponse)
async def get_interview_result(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the result of a completed interview.
    
    Includes:
    - Overall score
    - Summary and feedback
    - Strengths and improvement areas
    - Complete transcript
    - AI remarks
    """
    # Verify interview belongs to user
    interview = InterviewService.get_interview(db, interview_id, current_user.id)
    
    if interview.status != "completed":
        raise BadRequestException("Interview is not completed yet")
    
    # Get result
    result = db.query(InterviewResult).filter(
        InterviewResult.interview_id == interview_id
    ).first()
    
    if not result:
        raise NotFoundException("Interview result not found")
    
    return result


@router.get("/{interview_id}/transcript", response_model=dict)
async def get_interview_transcript(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the full Q&A transcript of a completed interview.
    
    Returns array of:
    - Question number
    - Question text
    - Answer text
    - Score
    - Feedback
    - Time taken
    """
    interview = InterviewService.get_interview(db, interview_id, current_user.id)
    
    if interview.status != "completed":
        raise BadRequestException("Interview is not completed yet")
    
    result = db.query(InterviewResult).filter(
        InterviewResult.interview_id == interview_id
    ).first()
    
    if not result:
        raise NotFoundException("Interview result not found")
    
    return {
        "interview_id": str(interview_id),
        "interview_type": interview.interview_type,
        "target_role": interview.target_role,
        "transcript": result.transcript
    }


@router.get("/stats/summary", response_model=dict)
async def get_interview_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's overall interview statistics.
    
    Includes:
    - Total interviews
    - Completed interviews
    - Average score
    - Improvement trend
    """
    # Get all completed interviews
    completed_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "completed"
    ).all()
    
    if not completed_interviews:
        return {
            "total_interviews": 0,
            "completed_interviews": 0,
            "average_score": 0,
            "highest_score": 0,
            "lowest_score": 0,
            "recent_scores": []
        }
    
    # Get results
    interview_ids = [i.id for i in completed_interviews]
    results = db.query(InterviewResult).filter(
        InterviewResult.interview_id.in_(interview_ids)
    ).all()
    
    scores = [r.overall_score for r in results]
    
    # Get recent 5 scores for trend
    recent_results = sorted(results, key=lambda x: x.created_at, reverse=True)[:5]
    recent_scores = [
        {
            "score": r.overall_score,
            "date": r.created_at.isoformat(),
            "interview_type": next((i.interview_type for i in completed_interviews if i.id == r.interview_id), "unknown")
        }
        for r in recent_results
    ]
    
    return {
        "total_interviews": len(completed_interviews),
        "completed_interviews": len(results),
        "average_score": sum(scores) / len(scores) if scores else 0,
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0,
        "recent_scores": recent_scores
    }
