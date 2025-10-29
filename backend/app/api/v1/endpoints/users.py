from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserPreference
from app.schemas.user import (
    UserProfile, UserUpdate,
    PlatformIntegration,
    UserPreferenceResponse, UserPreferenceUpdate
)
from app.schemas.common import ResponseBase
from app.core.exceptions import NotFoundException

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
    # TODO: Implement file upload to Supabase Storage
    # For now, just return success
    return ResponseBase(
        success=True,
        message="Avatar upload feature coming soon"
    )


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
