from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import HttpUrl

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserPreference
from app.schemas.user import (
    UserProfile, UserUpdate,
    PlatformIntegration,
    UserPreferenceResponse, UserPreferenceUpdate
)
from app.schemas.common import ResponseBase
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.storage_service import storage_service

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's full profile"""
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        # Convert Pydantic HttpUrl objects to strings for database storage
        if isinstance(value, HttpUrl):
            value = str(value)
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/avatar", response_model=ResponseBase)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise BadRequestException(
            f"Invalid file type. Allowed types: JPEG, PNG, GIF, WEBP"
        )
    
    # Validate file size (max 5MB)
    file_content = await file.read()
    max_size = 5 * 1024 * 1024  # 5MB
    if len(file_content) > max_size:
        raise BadRequestException("File size must be less than 5MB")
    
    # Reset file pointer
    await file.seek(0)
    
    # Upload to Supabase Storage
    try:
        public_url = storage_service.upload_avatar(
            file_content=file_content,
            user_id=current_user.id,
            filename=file.filename
        )
        
        # Update user's profile_picture_url in database
        current_user.profile_picture_url = public_url
        db.commit()
        db.refresh(current_user)
        
        return ResponseBase(
            success=True,
            message="Profile picture uploaded successfully"
        )
    except BadRequestException:
        raise
    except Exception as e:
        raise BadRequestException(f"Failed to upload profile picture: {str(e)}")


@router.get("/me/preferences", response_model=UserPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        raise NotFoundException("Preferences not found")
    
    return preferences


@router.put("/me/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    update_data: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        raise NotFoundException("Preferences not found")
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(preferences, field, value)
    
    db.commit()
    db.refresh(preferences)
    
    return preferences


@router.post("/me/integrations", response_model=ResponseBase)
async def connect_platforms(
    integration_data: PlatformIntegration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect external platforms (LeetCode, GitHub, etc.)"""
    
    update_dict = integration_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(current_user, field, value)
    
    db.commit()
    
    return ResponseBase(
        success=True,
        message="Platform integrations updated successfully"
    )


@router.get("/me/integrations", response_model=PlatformIntegration)
async def get_integrations(
    current_user: User = Depends(get_current_user)
):
    """Get connected platforms"""
    return PlatformIntegration(
        leetcode_username=current_user.leetcode_username,
        github_username=current_user.github_username,
        hackerrank_username=current_user.hackerrank_username,
        codechef_username=current_user.codechef_username,
        gfg_username=current_user.gfg_username
    )


@router.delete("/me", response_model=ResponseBase)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account permanently"""
    db.delete(current_user)
    db.commit()
    
    return ResponseBase(
        success=True,
        message="Account deleted successfully"
    )
