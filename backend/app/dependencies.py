from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationException
from app.models.user import User

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    Usage: current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise AuthenticationException("Invalid or expired token")
    
    if payload.get("type") != "access":
        raise AuthenticationException("Invalid token type")
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise AuthenticationException("Invalid token payload")
    
    # Query user from database
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    
    if user is None:
        raise AuthenticationException("User not found")
    
    if not user.is_active:
        raise AuthenticationException("User account is disabled")
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns None if not authenticated.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except:
        return None
