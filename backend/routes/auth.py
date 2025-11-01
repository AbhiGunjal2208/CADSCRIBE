"""
Authentication routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from typing import Optional, Callable
import bcrypt
import jwt
import logging

from services.database import db_service
from config import settings
from dependencies import get_current_user

router = APIRouter(tags=["auth"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    name: str
    password: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    created_at: datetime

    class Config:
        json_encoders: dict[type[datetime], Callable[[datetime], str]] = {
            datetime: lambda dt: dt.isoformat()
        }


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: UserResponse




@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate):
    """Create a new user account."""
    try:
        # Check if user exists
        existing_user = db_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
            
        # Hash password
        hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt())
        
        # Create user in database
        user_data_dict = {
            "email": user_data.email,
            "name": user_data.name,
            "password_hash": hashed_password.decode()
        }
        user_id = db_service.create_user(user_data_dict)
        
        # Create access token
        token_data = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        }
        access_token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        
        # Get created user
        created_user = db_service.get_user_by_email(user_data.email)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user_id,
                email=created_user["email"],
                name=created_user["name"],
                created_at=created_user["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """Authenticate user and return access token."""
    try:
        # Get user from database
        user = db_service.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
            
        # Check password
        is_valid = bcrypt.checkpw(
            login_data.password.encode(),
            user["password_hash"].encode()
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
            
        # Create access token
        token_data = {
            "sub": str(user["id"]),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        }
        access_token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(user["id"]),
                email=user["email"],
                name=user["name"],
                created_at=user["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/demo", response_model=TokenResponse)
async def demo_login():
    """Demo login endpoint that returns a valid token for demo user."""
    try:
        # Create access token for demo user
        token_data = {
            "sub": "demo-user",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        }
        access_token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id="demo-user",
                email="demo@cadscribe.com",
                name="Demo User",
                created_at=datetime.now(timezone.utc)
            )
        )
        
    except Exception as e:
        logger.error(f"Demo login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    try:
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            name=current_user["name"],
            created_at=current_user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
