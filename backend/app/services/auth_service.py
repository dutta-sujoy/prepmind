from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid

from app.models.user import User, UserPreference
from app.models.token import RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserCreate
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.exceptions import (
    AuthenticationException,
    ConflictException,
    NotFoundException,
    BadRequestException
)
from app.config import settings


class AuthService:
    
    @staticmethod
    def register_user(db: Session, register_data: RegisterRequest) -> User:
        """Register a new user"""
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == register_data.email).first()
        if existing_user:
            raise ConflictException("Email already registered")
        
        # Create user
        user = User(
            email=register_data.email,
            hashed_password=get_password_hash(register_data.password),
            full_name=register_data.full_name,
            college=register_data.college,
            branch=register_data.branch,
            graduation_year=register_data.graduation_year,
            target_role=register_data.target_role,
        )
        
        db.add(user)
        db.flush()  # Flush to get user.id
        
        # Create default preferences
        preferences = UserPreference(user_id=user.id)
        db.add(preferences)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> Tuple[User, str, str]:
        """Authenticate user and return tokens"""
        
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise AuthenticationException("Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("Account is disabled")
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token_str = create_refresh_token({"sub": str(user.id)})
        
        # Save refresh token to database
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(refresh_token)
        db.commit()
        
        return user, access_token, refresh_token_str
    
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token_str: str) -> Tuple[str, str]:
        """Generate new access token using refresh token"""
        
        # Decode refresh token
        payload = decode_token(refresh_token_str)
        if payload is None or payload.get("type") != "refresh":
            raise AuthenticationException("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
        
        # Check if refresh token exists and is valid
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.user_id == uuid.UUID(user_id),
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not refresh_token:
            raise AuthenticationException("Invalid or expired refresh token")
        
        # Check if user exists and is active
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")
        
        # Create new tokens
        new_access_token = create_access_token({"sub": user_id})
        new_refresh_token_str = create_refresh_token({"sub": user_id})
        
        # Revoke old refresh token
        refresh_token.is_revoked = True
        
        # Save new refresh token
        new_refresh_token = RefreshToken(
            user_id=user.id,
            token=new_refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(new_refresh_token)
        db.commit()
        
        return new_access_token, new_refresh_token_str
    
    
    @staticmethod
    def logout_user(db: Session, user_id: uuid.UUID, refresh_token_str: str):
        """Logout user by revoking refresh token"""
        
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.user_id == user_id
        ).first()
        
        if refresh_token:
            refresh_token.is_revoked = True
            db.commit()
    
    
    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str):
        """Change user password"""
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise BadRequestException("Current password is incorrect")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        
        # Revoke all refresh tokens (force re-login)
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        
        db.commit()
