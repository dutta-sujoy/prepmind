from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_type = Column(String(20), nullable=True)  # pdf, docx
    
    # Extracted content
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSONB, nullable=True)  # Structured resume data
    
    # Analysis results
    ats_score = Column(Integer, nullable=True)  # 0-100
    analysis_result = Column(JSONB, nullable=True)  # Changed from 'analysis' to 'analysis_result'
    
    # Metadata
    is_primary = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
