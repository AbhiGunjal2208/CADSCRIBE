"""
AI service routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from services.ai_service import ai_service
from services.database import db_service
from services.project_service import project_service
from dependencies import get_current_user
from models.schema import MessageRole

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])
security = HTTPBearer()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    project_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    message: ChatMessage
    suggestions: Optional[List[str]] = None
    code_generated: Optional[str] = None


class CodeGenerateRequest(BaseModel):
    """Code generation request."""
    description: str
    engine: str = "freecad"  # Only FreeCAD headless mode is supported
    parameters: Optional[Dict[str, Any]] = None


class CodeGenerateResponse(BaseModel):
    """Code generation response."""
    success: bool
    generated_code: Optional[str] = None
    engine: str
    parameters: Dict[str, Any]
    confidence: float
    explanation: str
    error: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Chat with AI assistant."""
    try:
        user_id = current_user["id"]
        
        # Ensure project exists or create it
        project_id = request.project_id or f"chat-{user_id}-{datetime.now().strftime('%Y%m%d')}"
        
        project = project_service.get_project_by_id(project_id)
        if not project:
            # Create new project for this chat session
            project_data = {
                "project_id": project_id,
                "project_name": f"Chat Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "created_by": user_id,
                "metadata": {
                    "description": "Auto-created from chat session",
                    "chat_session": True
                }
            }
            project_service.create_project(project_data)
        
        # Save user message to new messages collection
        user_message_data: Dict[str, Any] = {
            "project_id": project_id,
            "user_id": user_id,
            "role": MessageRole.USER.value,
            "content": request.message,
            "timestamp": datetime.utcnow(),
            "metadata": request.context or {}
        }
        project_service.create_message(user_message_data)
        
        # Generate AI response with context including project_id and user_id
        context = request.context or {}
        context['project_id'] = project_id
        context['user_id'] = user_id
        context['engine'] = 'freecad'  # Force FreeCAD headless mode
        context['headless'] = True  # Explicit headless flag
        
        ai_result = await ai_service.generate_cad_code(
            request.message,
            context
        )
        
        if ai_result["success"]:
            # Create AI response message
            ai_response_content = f"I've generated CAD code using {ai_result['source_model']} for your request."
            if ai_result.get("generated_code"):
                ai_response_content += f"\n\nHere's the generated code:\n```python\n{ai_result['generated_code']}\n```"
            
            if ai_result.get("s3_url"):
                version_info = f" (version {ai_result['script_version']})" if ai_result.get('script_version') else ""
                ai_response_content += f"\n\n📁 Code saved to S3{version_info}: {ai_result['s3_url']}"
            
            ai_message_data: Dict[str, Any] = {
                "project_id": project_id,
                "user_id": user_id,
                "role": MessageRole.ASSISTANT.value,
                "content": ai_response_content,
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "source_model": ai_result["source_model"],
                    "confidence": ai_result["confidence"],
                    "response_time": ai_result["response_time"],
                    "s3_url": ai_result.get("s3_url"),
                    "script_version": ai_result.get("script_version"),
                    "s3_result": ai_result.get("s3_result"),
                    "timestamp": ai_result["timestamp"]
                }
            }
            project_service.create_message(ai_message_data)
            
            return ChatResponse(
                message=ChatMessage(
                    role="assistant",
                    content=ai_response_content,
                    timestamp=ai_result["timestamp"]
                ),
                suggestions=[
                    "Generate a cube with holes",
                    "Create a parametric bracket",
                    "Make a threaded bolt",
                    "Design a custom flange"
                ],
                code_generated=ai_result.get("generated_code")
            )
        else:
            # Handle error case
            error_message = f"I encountered an error generating your CAD code: {ai_result.get('error', 'Unknown error')}"
            
            ai_message_data: Dict[str, Any] = {
                "project_id": project_id,
                "user_id": user_id,
                "role": MessageRole.ASSISTANT.value,
                "content": error_message,
                "timestamp": datetime.utcnow(),
                "metadata": {"error": ai_result.get("error"), "timestamp": ai_result["timestamp"]}
            }
            project_service.create_message(ai_message_data)
            
            return ChatResponse(
                message=ChatMessage(
                    role="assistant",
                    content=error_message,
                    timestamp=ai_result["timestamp"]
                ),
                suggestions=[
                    "Try a simpler description",
                    "Specify dimensions clearly",
                    "Use basic shapes first"
                ],
                code_generated=None
            )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.post("/generate-code", response_model=CodeGenerateResponse)
async def generate_code(
    request: CodeGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate CAD code from description."""
    try:
        user_id = current_user["id"]
        
        # Generate code using AI service - Force FreeCAD headless mode
        context = {
            "engine": "freecad",  # Always use FreeCAD headless
            "headless": True,  # Explicit headless flag
            "parameters": request.parameters or {},
            "user_id": user_id,
            "project_id": "code-generation"  # Default project for standalone code generation
        }
        
        ai_result = await ai_service.generate_cad_code(
            request.description,
            context
        )
        
        if ai_result["success"]:
            return CodeGenerateResponse(
                success=True,
                generated_code=ai_result["generated_code"],
                engine=ai_result["source_model"],
                parameters=request.parameters or {},
                confidence=ai_result["confidence"] or 0.8,
                explanation=f"Generated using {ai_result['source_model']} in {ai_result['response_time']:.2f}s"
            )
        else:
            return CodeGenerateResponse(
                success=False,
                generated_code=None,
                engine=request.engine,
                parameters=request.parameters or {},
                confidence=0.0,
                explanation="Code generation failed",
                error=ai_result.get("error", "Unknown error")
            )
        
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate code"
        )


from typing import Dict

@router.get("/chat-history/{project_id}")
async def get_chat_history(
    project_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, List[ChatMessage]]:
    """Get chat history for a project."""
    try:
        user_id = current_user["id"]
        
        messages = db_service.get_chat_history(project_id, 0, 100)
        
        chat_messages: List[ChatMessage] = []
        for msg in messages:
            chat_messages.append(ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["created_at"].isoformat()
            ))
        
        return {"messages": chat_messages}
        
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history"
        )


@router.get("/engines")
async def get_supported_engines():
    """Get list of supported CAD engines."""
    return {
        "engines": [
            {
                "id": "freecad",
                "name": "FreeCAD Headless",
                "description": "Python scripting for FreeCAD in headless mode (no GUI)",
                "language": "Python",
                "mode": "headless",
                "supported": True,
                "default": True
            }
        ],
        "note": "Currently only FreeCAD headless mode is supported for server-side execution"
    }


@router.get("/metrics")
async def get_ai_performance_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get AI service performance metrics."""
    try:
        metrics = ai_service.get_performance_metrics()
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics"
        )
