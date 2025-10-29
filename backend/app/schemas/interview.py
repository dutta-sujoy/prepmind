from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# Interview Creation
class InterviewCreate(BaseModel):
    interview_type: str = Field(..., pattern="^(technical|hr|behavioral|mixed)$")
    target_role: str = Field(..., min_length=2, max_length=100)
    technologies: List[str] = Field(..., min_items=1, max_items=10)
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    num_questions: int = Field(..., ge=3, le=15)
    
    class Config:
        json_schema_extra = {
            "example": {
                "interview_type": "technical",
                "target_role": "Full Stack Developer",
                "technologies": ["React", "Node.js", "MongoDB"],
                "difficulty": "medium",
                "num_questions": 5
            }
        }


# Question Schema
class QuestionSchema(BaseModel):
    id: int
    text: str
    category: str
    difficulty: str
    expected_points: List[str]


# Interview Response
class InterviewResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    interview_type: str
    target_role: str
    technologies: List[str]
    difficulty: str
    num_questions: int
    questions: List[Dict[str, Any]]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Interview List Item
class InterviewListItem(BaseModel):
    id: uuid.UUID
    interview_type: str
    target_role: str
    technologies: List[str]
    num_questions: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# WebSocket Messages
class WSStartInterview(BaseModel):
    interview_id: str
    user_id: str


class WSAnswer(BaseModel):
    question_number: int
    answer_text: str
    time_taken: int  # seconds


class WSQuestion(BaseModel):
    type: str = "question"
    question_number: int
    question_text: str
    total_questions: int
    time_limit: Optional[int] = 180  # 3 minutes


class WSFeedback(BaseModel):
    type: str = "feedback"
    question_number: int
    feedback: str
    score: int
    next_question: Optional[str] = None


class WSComplete(BaseModel):
    type: str = "interview_complete"
    overall_score: int
    summary: str
    detailed_feedback: Dict[str, Any]
    improvement_areas: List[str]
    strengths: List[str]


# Interview Result
class InterviewResultResponse(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    overall_score: int
    summary: str
    detailed_feedback: Dict[str, Any]
    improvement_areas: List[str]
    strengths: List[str]
    transcript: List[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True
