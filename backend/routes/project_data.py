"""
Project data routes for the new project-centric schema.
Provides structured access to project messages, files, and logs.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from services.project_service import project_service
from dependencies import get_current_user
from models.schema import ProjectStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["project-data"])
security = HTTPBearer()


@router.get("/{project_id}/messages")
async def get_project_messages(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all messages for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_id.startswith("demo-project-"):
            project = project_service.get_project_by_id(project_id)
            if not project or project["created_by"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get messages from new messages collection
        if project_id.startswith("demo-project-"):
            # Return demo messages
            messages = []
            if project_id == "demo-project-1":
                messages = [
                    {
                        "id": "demo-msg-1",
                        "role": "user",
                        "content": "Create a simple cube",
                        "timestamp": "2024-01-15T10:00:00Z",
                        "metadata": {}
                    },
                    {
                        "id": "demo-msg-2", 
                        "role": "assistant",
                        "content": "I'll create a parametric cube for you. Here's the generated code:\n\n```python\nimport cadquery as cq\n\n# Generate a cube\ncube = cq.Workplane(\"XY\").box(50, 30, 20)\n\n# Show the result\nshow_object(cube)\n```",
                        "timestamp": "2024-01-15T10:01:00Z",
                        "metadata": {"source_model": "Demo", "confidence": 1.0}
                    }
                ]
            elif project_id == "demo-project-2":
                messages = [
                    {
                        "id": "demo-msg-3",
                        "role": "user", 
                        "content": "Design a flange with bolt holes",
                        "timestamp": "2024-01-14T14:00:00Z",
                        "metadata": {}
                    },
                    {
                        "id": "demo-msg-4",
                        "role": "assistant",
                        "content": "I'll create a parametric flange design:\n\n```python\nimport cadquery as cq\n\n# Create flange with bolt holes\nflange = cq.Workplane(\"XY\").circle(50).extrude(10)\nflange = flange.faces(\">Z\").circle(10).cutThruAll()\n\nshow_object(flange)\n```",
                        "timestamp": "2024-01-14T14:01:00Z",
                        "metadata": {"source_model": "Demo", "confidence": 1.0}
                    }
                ]
        else:
            messages = project_service.get_project_messages(project_id)
            # Format messages for response
            for message in messages:
                if isinstance(message.get("timestamp"), datetime):
                    message["timestamp"] = message["timestamp"].isoformat()
        
        return {
            "success": True,
            "project_id": project_id,
            "messages": messages,
            "total_messages": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project messages error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project messages"
        )


@router.get("/{project_id}/files")
async def get_project_files(
    project_id: str,
    file_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all files for a project, optionally filtered by type."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_id.startswith("demo-project-"):
            project = project_service.get_project_by_id(project_id)
            if not project or project["created_by"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get files from new files collection
        if project_id.startswith("demo-project-"):
            # Return demo files
            files = [
                {
                    "id": f"demo-file-{project_id}",
                    "project_id": project_id,
                    "version": 1,
                    "file_type": "input",
                    "s3_path": f"s3://demo-bucket/input/{project_id}/{project_id}_v1.py",
                    "timestamp": "2024-01-15T10:00:00Z",
                    "metadata": {
                        "file_name": f"{project_id}_v1.py",
                        "ai_model": "Demo",
                        "generated_by": "demo"
                    }
                }
            ]
            if file_type:
                files = [f for f in files if f["file_type"] == file_type]
        else:
            files = project_service.get_project_files(project_id, file_type)
            # Format files for response
            for file in files:
                if isinstance(file.get("timestamp"), datetime):
                    file["timestamp"] = file["timestamp"].isoformat()
        
        return {
            "success": True,
            "project_id": project_id,
            "files": files,
            "total_files": len(files),
            "file_type_filter": file_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project files error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project files"
        )


@router.get("/{project_id}/logs")
async def get_project_logs(
    project_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get logs for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_id.startswith("demo-project-"):
            project = project_service.get_project_by_id(project_id)
            if not project or project["created_by"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get logs from new logs collection
        if project_id.startswith("demo-project-"):
            # Return demo logs
            logs = [
                {
                    "id": f"demo-log-{project_id}",
                    "project_id": project_id,
                    "version": 1,
                    "s3_log_path": f"s3://demo-bucket/logs/{project_id}/{project_id}_info_20240115_100000.log",
                    "log_summary": "Model generated successfully.",
                    "timestamp": "2024-01-15T10:05:00Z",
                    "metadata": {}
                }
            ]
        else:
            logs = project_service.get_project_logs(project_id, limit)
            # Format logs for response
            for log in logs:
                if isinstance(log.get("timestamp"), datetime):
                    log["timestamp"] = log["timestamp"].isoformat()
        
        return {
            "success": True,
            "project_id": project_id,
            "logs": logs,
            "total_logs": len(logs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project logs"
        )


@router.get("/{project_id}/complete")
async def get_complete_project_data(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get complete project data including messages, files, and logs."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_id.startswith("demo-project-"):
            project = project_service.get_project_by_id(project_id)
            if not project or project["created_by"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get complete project data
        if project_id.startswith("demo-project-"):
            # Return demo project data
            complete_data = {
                "project": {
                    "project_id": project_id,
                    "project_name": project_id.replace("-", " ").title(),
                    "created_by": user_id,
                    "status": ProjectStatus.COMPLETED.value,
                    "current_version": 1,
                    "ai_model_used": "Demo",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T10:00:00Z",
                    "metadata": {
                        "description": f"Demo {project_id.replace('-', ' ')} project",
                        "demo": True
                    }
                },
                "messages": [],
                "files": [],
                "logs": []
            }
            
            # Add demo data
            if project_id == "demo-project-1":
                complete_data["messages"] = [
                    {
                        "id": "demo-msg-1",
                        "role": "user",
                        "content": "Create a simple cube",
                        "timestamp": "2024-01-15T10:00:00Z"
                    }
                ]
            
        else:
            complete_data = project_service.get_project_with_data(project_id)
            if not complete_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Format datetime objects
            def format_datetime_in_dict(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, datetime):
                            obj[key] = value.isoformat()
                        elif isinstance(value, (dict, list)):
                            format_datetime_in_dict(value)
                elif isinstance(obj, list):
                    for item in obj:
                        format_datetime_in_dict(item)
            
            format_datetime_in_dict(complete_data)
        
        return {
            "success": True,
            "data": complete_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get complete project data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get complete project data"
        )


@router.get("/{project_id}/summary")
async def get_project_summary(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get project summary with counts and latest activity."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_id.startswith("demo-project-"):
            project = project_service.get_project_by_id(project_id)
            if not project or project["created_by"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        else:
            # Mock project for demo
            project = {
                "project_id": project_id,
                "project_name": project_id.replace("-", " ").title(),
                "created_by": user_id,
                "status": ProjectStatus.COMPLETED.value,
                "current_version": 1,
                "ai_model_used": "Demo"
            }
        
        # Get counts
        if project_id.startswith("demo-project-"):
            summary = {
                "project": project,
                "message_count": 2,
                "file_count": 1,
                "log_count": 1,
                "latest_activity": "2024-01-15T10:01:00Z",
                "files_by_type": {
                    "input": 1,
                    "output": 0,
                    "log": 0,
                    "processed": 0
                }
            }
        else:
            messages = project_service.get_project_messages(project_id)
            files = project_service.get_project_files(project_id)
            logs = project_service.get_project_logs(project_id, limit=1)
            
            # Count files by type
            files_by_type = {"input": 0, "output": 0, "log": 0, "processed": 0}
            for file in files:
                file_type = file.get("file_type", "unknown")
                if file_type in files_by_type:
                    files_by_type[file_type] += 1
            
            # Get latest activity timestamp
            latest_activity = project.get("updated_at")
            if messages and messages[-1].get("timestamp"):
                msg_time = messages[-1]["timestamp"]
                if isinstance(msg_time, datetime):
                    msg_time = msg_time.isoformat()
                if not latest_activity or msg_time > latest_activity:
                    latest_activity = msg_time
            
            summary = {
                "project": project,
                "message_count": len(messages),
                "file_count": len(files),
                "log_count": len(logs),
                "latest_activity": latest_activity,
                "files_by_type": files_by_type
            }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project summary"
        )
