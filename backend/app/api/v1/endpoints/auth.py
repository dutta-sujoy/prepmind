from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    RefreshTokenRequest, TokenResponse,
    ChangePasswordRequest
)
from app.schemas.common import ResponseBase

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    - **college**: College/University name (optional)
    - **branch**: Branch/Stream (optional)
    - **graduation_year**: Expected graduation year (optional)
    - **target_role**: Desired job role (optional)
    """
    user = AuthService.register_user(db, register_data)
    
    return RegisterResponse(
        success=True,
        message="Registration successful. Please verify your email.",
        user_id=user.id,
        email=user.email
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns JWT access token (30 min) and refresh token (7 days).
    """
    user, access_token, refresh_token = AuthService.authenticate_user(db, login_data)
    
    return LoginResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture_url": user.profile_picture_url
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Returns new access token and refresh token.
    Old refresh token is revoked.
    """
    access_token, refresh_token = AuthService.refresh_access_token(
        db, refresh_data.refresh_token
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/logout", response_model=ResponseBase)
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token.
    """
    AuthService.logout_user(db, current_user.id, refresh_data.refresh_token)
    
    return ResponseBase(
        success=True,
        message="Logout successful"
    )


@router.post("/change-password", response_model=ResponseBase)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Requires current password for verification.
    All refresh tokens will be revoked (force re-login).
    """
    AuthService.change_password(
        db,
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    
    return ResponseBase(
        success=True,
        message="Password changed successfully. Please login again."
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "college": current_user.college,
        "target_role": current_user.target_role,
        "email_verified": current_user.email_verified,
        "is_premium": current_user.is_premium
    }
