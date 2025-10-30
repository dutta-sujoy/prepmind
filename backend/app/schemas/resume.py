from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ResumeUpload(BaseModel):
    """Resume upload request"""
    file_name: str
    is_primary: bool = False


class ResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    is_primary: bool
    parsed_data: Optional[Dict[str, Any]] = None
    ats_score: Optional[int] = None
    analysis_result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResumeListItem(BaseModel):
    id: uuid.UUID
    file_name: str
    file_type: str
    is_primary: bool
    ats_score: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeAnalysis(BaseModel):
    ats_score: int = Field(..., ge=0, le=100)
    overall_rating: str  # excellent, good, average, needs_improvement
    
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str] = []
    keywords: List[str] = []
    missing_sections: List[str] = []
    
    skills_analysis: Dict[str, Any]
    experience_analysis: Dict[str, Any]
    education_analysis: Dict[str, Any]
    content_quality: Optional[Dict[str, Any]] = None
    
    recommendations: List[str]
    keyword_match: Dict[str, Any]
    
    detailed_feedback: str


class ParsedResumeData(BaseModel):
    """Structured data extracted from resume"""
    contact_info: Dict[str, Any]
    summary: Optional[str] = None
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    projects: List[Dict[str, Any]]
    achievements: List[str]
    languages: List[str]
