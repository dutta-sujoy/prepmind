from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, 
        index=True
    )
    
    # Interview Configuration
    interview_type = Column(String(20), nullable=False)  # technical, hr, behavioral, mixed
    target_role = Column(String(100), nullable=False)
    technologies = Column(ARRAY(Text))
    difficulty = Column(String(20))  # easy, medium, hard
    num_questions = Column(Integer, nullable=False)
    
    # Pre-generated Questions
    questions = Column(JSONB)  # [{id, text, category, expected_answer}]
    
    # Status
    status = Column(String(20), default="draft", index=True)  # draft, in_progress, completed, abandoned
    
    # Session Metadata
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    result = relationship("InterviewResult", back_populates="interview", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Interview {self.interview_type} - {self.status}>"


class InterviewResult(Base):
    __tablename__ = "interview_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False, 
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, 
        index=True
    )
    
    # Overall Scoring
    overall_score = Column(Integer)
    question_scores = Column(ARRAY(Integer))
    
    # Detailed Feedback
    summary = Column(Text)
    detailed_feedback = Column(JSONB)  # {technical_depth, communication, problem_solving, confidence}
    improvement_areas = Column(ARRAY(Text))
    strengths = Column(ARRAY(Text))
    
    # Transcript
    transcript = Column(JSONB)  # [{question_number, question_text, answer_text, score, feedback}]
    
    # Voice Analysis
    voice_analysis = Column(JSONB)  # {pace_wpm, filler_words, confidence_score, clarity}
    
    # AI Remarks
    ai_remarks = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    interview = relationship("Interview", back_populates="result")
    user = relationship("User", back_populates="interview_results")
    
    def __repr__(self):
        return f"<InterviewResult score={self.overall_score}>"
