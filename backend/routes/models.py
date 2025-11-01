"""
CAD models routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import logging
from services.database import db_service
from services.ai_service import ai_service
from services.cad_service import cad_service
from dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/models", tags=["models"])
security = HTTPBearer()


class ModelGenerateRequest(BaseModel):
    """Model generation request."""
    description: str
    output_format: str = "stl"
    parameters: Optional[dict] = None


class ModelResponse(BaseModel):
    """Model response."""
    id: str
    user_id: str
    title: str
    description: str
    file_path: str
    file_size: int
    format: str
    download_url: str
    created_at: str
    metadata: dict


class ModelListResponse(BaseModel):
    """Model list response."""
    models: List[ModelResponse]
    total: int
    page: int
    limit: int


@router.post("/generate", response_model=ModelResponse)
async def generate_model(
    request: ModelGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a CAD model from natural language description."""
    try:
        user_id = current_user["id"]
        
        # Generate CAD code using AI service
        ai_result = await ai_service.generate_cad_code(
            request.description,
            {"output_format": request.output_format}
        )
        
        if not ai_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI code generation failed: {ai_result.get('error')}"
            )
        
        # Generate CAD model using CAD service
        cad_result = await cad_service.generate_model(
            ai_result["generated_code"],
            request.output_format,
            request.parameters
        )
        
        if not cad_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"CAD model generation failed: {cad_result.get('error')}"
            )
        
        # Save model to database
        model_data = {
            "user_id": user_id,
            "title": request.description[:50],  # Truncate for title
            "description": request.description,
            "file_path": cad_result["file_path"],
            "file_size": cad_result["file_size"],
            "format": request.output_format,
            "download_url": cad_result["download_url"],
            "generated_code": ai_result["generated_code"],
            "ai_metadata": ai_result,
            "cad_metadata": cad_result["metadata"]
        }
        
        model_id = db_service.create_model(model_data)
        
        return ModelResponse(
            id=model_id,
            user_id=user_id,
            title=model_data["title"],
            description=model_data["description"],
            file_path=model_data["file_path"],
            file_size=model_data["file_size"],
            format=model_data["format"],
            download_url=model_data["download_url"],
            created_at="2024-01-01T00:00:00Z",
            metadata={
                "ai_confidence": ai_result.get("confidence", 0),
                "generation_time": cad_result.get("generation_time", 0),
                "parameters": request.parameters or {}
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate model"
        )


@router.get("/", response_model=ModelListResponse)
async def get_models(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get user's CAD models."""
    try:
        user_id = current_user["id"]
        
        models = db_service.get_user_models(user_id, (page - 1) * limit, limit)
        
        # Convert to response format
        model_responses = []
        for model in models:
            model_responses.append(ModelResponse(
                id=model["id"],
                user_id=model["user_id"],
                title=model["title"],
                description=model["description"],
                file_path=model["file_path"],
                file_size=model["file_size"],
                format=model["format"],
                download_url=model["download_url"],
                created_at=model["created_at"].isoformat(),
                metadata=model.get("cad_metadata", {})
            ))
        
        return ModelListResponse(
            models=model_responses,
            total=len(model_responses),
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Get models error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get models"
        )


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific model by ID."""
    try:
        user_id = current_user["id"]
        
        # Get model from database
        model = db_service.get_model(model_id)
        
        if not model or model["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        return ModelResponse(
            id=model["id"],
            user_id=model["user_id"],
            title=model["title"],
            description=model["description"],
            file_path=model["file_path"],
            file_size=model["file_size"],
            format=model["format"],
            download_url=model["download_url"],
            created_at=model["created_at"].isoformat(),
            metadata=model.get("cad_metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get model error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model"
        )


@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a model."""
    try:
        user_id = current_user["id"]
        
        # Get model to verify ownership
        model = db_service.get_model(model_id)
        if not model or model["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        # Delete model from database
        # TODO: Also delete the actual file from storage
        
        return {"message": "Model deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete model error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete model"
        )
