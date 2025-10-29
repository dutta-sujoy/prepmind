from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile Information
    full_name = Column(String(255), nullable=False)
    college = Column(String(255))
    branch = Column(String(100))
    graduation_year = Column(Integer)
    target_role = Column(String(100))
    profile_picture_url = Column(Text)
    bio = Column(Text)
    
    # Contact Information
    phone = Column(String(20))
    linkedin_url = Column(String(255))
    github_url = Column(String(255))
    portfolio_url = Column(String(255))
    
    # Platform Integrations
    leetcode_username = Column(String(100))
    github_username = Column(String(100))
    hackerrank_username = Column(String(100))
    codechef_username = Column(String(100))
    gfg_username = Column(String(100))
    
    # Account Status
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    interview_results = relationship("InterviewResult", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    # These will be added later when we create those models
    # roadmaps = relationship("CareerRoadmap", back_populates="user", cascade="all, delete-orphan")
    # skill_progress = relationship("SkillProgress", back_populates="user", cascade="all, delete-orphan")
    # projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    # cover_letters = relationship("CoverLetter", back_populates="user", cascade="all, delete-orphan")
    # job_bookmarks = relationship("JobBookmark", back_populates="user", cascade="all, delete-orphan")
    # job_applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    # job_alerts = relationship("JobAlert", back_populates="user", cascade="all, delete-orphan")
    # analytics = relationship("UserAnalytics", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),  # ← THIS WAS MISSING
        nullable=False, 
        unique=True, 
        index=True
    )
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    job_alerts = Column(Boolean, default=True)
    roadmap_reminders = Column(Boolean, default=True)
    interview_reminders = Column(Boolean, default=True)
    
    # UI Preferences
    theme = Column(String(20), default="light")  # light, dark, auto
    language = Column(String(10), default="en")
    
    # Privacy Settings
    profile_visibility = Column(String(20), default="private")  # private, public
    show_progress_publicly = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference for user_id={self.user_id}>"
