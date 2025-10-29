from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional
from datetime import datetime
import uuid


# User Creation (for internal use)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    college: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    target_role: Optional[str] = None


# User Update
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    college: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    target_role: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None


# Platform Integration
class PlatformIntegration(BaseModel):
    leetcode_username: Optional[str] = None
    github_username: Optional[str] = None
    hackerrank_username: Optional[str] = None
    codechef_username: Optional[str] = None
    gfg_username: Optional[str] = None


# User Response (Public)
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    college: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    target_role: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    email_verified: bool
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Profile (Detailed)
class UserProfile(UserResponse):
    leetcode_username: Optional[str] = None
    github_username: Optional[str] = None
    hackerrank_username: Optional[str] = None
    codechef_username: Optional[str] = None
    gfg_username: Optional[str] = None
    last_login_at: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True


# User Preferences
class UserPreferenceUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    job_alerts: Optional[bool] = None
    roadmap_reminders: Optional[bool] = None
    interview_reminders: Optional[bool] = None
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    language: Optional[str] = None
    profile_visibility: Optional[str] = Field(None, pattern="^(private|public)$")
    show_progress_publicly: Optional[bool] = None


class UserPreferenceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email_notifications: bool
    push_notifications: bool
    job_alerts: bool
    roadmap_reminders: bool
    interview_reminders: bool
    theme: str
    language: str
    profile_visibility: str
    show_progress_publicly: bool
    
    class Config:
        from_attributes = True
