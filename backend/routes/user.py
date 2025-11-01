"""
User management routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from services.database import db_service
from dependencies import get_current_user
import bcrypt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["user"])
security = HTTPBearer()


class UserProfile(BaseModel):
    """User profile model."""
    name: str
    email: str
    avatar: Optional[str] = None


class UserSettings(BaseModel):
    """User settings model."""
    accentColor: str = "blue"
    fontSize: str = "normal"
    sidebarBehavior: str = "visible"
    defaultUnits: str = "mm"
    gridVisible: bool = True
    defaultMaterial: str = "plastic"
    defaultExportFormat: str = "step"
    emailNotifications: bool = True
    productUpdates: bool = True
    twoFactorAuth: bool = False


class SessionInfo(BaseModel):
    """Session information model."""
    device: str
    location: str
    lastLogin: str


@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information."""
    try:
        return {
            "name": current_user["name"],
            "email": current_user["email"],
            "avatar": current_user.get("avatar"),
            "created_at": current_user["created_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfile,
    current_user: dict = Depends(get_current_user)
) -> dict:
    try:
        user_id = current_user["id"]
        
        # Update user profile in database
        update_data = {
            "name": profile_data.name,
            "email": profile_data.email
        }
        
        if profile_data.avatar:
            update_data["avatar"] = profile_data.avatar
        
        success = db_service.update_user(user_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile in database"
            )
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": {
                "name": profile_data.name,
                "email": profile_data.email,
                "avatar": profile_data.avatar
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/settings")
async def update_user_settings(
    settings_data: UserSettings,
    current_user: dict = Depends(get_current_user)
):
    """Update user settings."""
    try:
        user_id = current_user["id"]
        
        # Update user preferences in database
        preferences = {
            "theme": settings_data.accentColor,  # Map accentColor to theme
            "fontSize": settings_data.fontSize,
            "sidebarBehavior": settings_data.sidebarBehavior,
            "defaultUnits": settings_data.defaultUnits,
            "gridVisible": settings_data.gridVisible,
            "defaultMaterial": settings_data.defaultMaterial,
            "defaultExportFormat": settings_data.defaultExportFormat,
            "emailNotifications": settings_data.emailNotifications,
            "productUpdates": settings_data.productUpdates,
            "twoFactorAuth": settings_data.twoFactorAuth
        }
        
        update_data = {"preferences": preferences}
        success = db_service.update_user(user_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update settings in database"
            )
        
        return {
            "success": True,
            "message": "Settings updated successfully",
            "settings": preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )


@router.get("/sessions")
async def get_user_sessions(current_user: dict = Depends(get_current_user)):
    """Get user session history."""
    try:
        user_id = current_user["id"]
        
        # TODO: Implement actual session tracking
        sessions = [
            {
                "device": "Chrome on Windows",
                "location": "New York, US",
                "lastLogin": "2024-01-15T10:00:00Z"
            }
        ]
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session history"
        )


@router.post("/change-password")
async def change_password(
    password_data: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Change user password."""
    try:
        user_id = current_user["id"]
        
        # Validate input
        if "current_password" not in password_data or "new_password" not in password_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password and new password are required"
            )
        
        # Get current user from database
        user = db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        is_valid = bcrypt.checkpw(
            password_data["current_password"].encode(),
            user["password_hash"].encode()
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(
            password_data["new_password"].encode(),
            bcrypt.gensalt()
        )
        
        # Update password in database
        success = db_service.update_user(user_id, {
            "password_hash": new_password_hash.decode()
        })
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password in database"
            )
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/delete")
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    """Delete user account."""
    try:
        user_id = current_user["id"]
        
        # Delete user and all associated data
        success = db_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete account"
            )
        
        return {
            "success": True,
            "message": "Account deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete account error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
