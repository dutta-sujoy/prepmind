from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid


# Registration
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    college: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=2020, le=2030)
    target_role: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@college.edu",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "college": "KIIT University",
                "branch": "Computer Science",
                "graduation_year": 2025,
                "target_role": "Full Stack Developer"
            }
        }


class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: uuid.UUID
    email: EmailStr


# Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@college.edu",
                "password": "SecurePass123!"
            }
        }


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Login successful",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "student@college.edu",
                    "full_name": "John Doe"
                }
            }
        }


# Token Refresh
class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Password Reset
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


# Email Verification
class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# Change Password
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
