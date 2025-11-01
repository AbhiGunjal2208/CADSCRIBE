"""
Project management routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from services.database import db_service
from services.project_service import project_service
from services.s3_service import s3_service
from dependencies import get_current_user
from models.schema import ProjectStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])
security = HTTPBearer()


class ProjectCreate(BaseModel):
    """Project creation model."""
    name: str
    description: str
    engine: str = "freecad"
    parameters: Dict[str, Any] = {}


class ProjectResponse(BaseModel):
    """Project response model."""
    id: str
    name: str
    description: str
    engine: str
    parameters: Dict[str, Any]
    lastModified: str
    created_at: str


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    context: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects for the current user."""
    try:
        user_id = current_user["id"]
        
        # Get projects from new project service
        projects = project_service.get_user_projects(user_id)
        
        # Transform to expected format
        formatted_projects = []
        for project in projects:
            formatted_project = {
                "id": project.get("id", project.get("project_id", "")),
                "name": project.get("title", project.get("project_name", "")),
                "description": project.get("description", project.get("metadata", {}).get("description", "")),
                "engine": "freecad",  # Default engine
                "parameters": project.get("metadata", {}).get("parameters", {}),
                "lastModified": project["updated_at"].isoformat() if isinstance(project["updated_at"], datetime) else project["updated_at"],
                "created_at": project["created_at"].isoformat() if isinstance(project["created_at"], datetime) else project["created_at"],
                "status": project.get("status", ProjectStatus.DRAFT.value),
                "current_version": project.get("current_version", 0),
                "ai_model_used": project.get("ai_model_used"),
                "messages": []
            }
            formatted_projects.append(formatted_project)
        
        # If this is the demo user, always include sample projects
        if user_id == "demo-user":
            demo_projects = [
                {
                    "id": "demo-project-1",
                    "name": "Sample Cube",
                    "description": "A simple parametric cube",
                    "engine": "freecad",
                    "parameters": {"width": 50, "height": 30, "depth": 20, "thickness": 2},
                    "lastModified": "2024-01-15",
                    "created_at": "2024-01-01T00:00:00Z",
                    "status": ProjectStatus.COMPLETED.value,
                    "current_version": 1,
                    "ai_model_used": "Demo",
                    "messages": []
                },
                {
                    "id": "demo-project-2", 
                    "name": "Sample Flange",
                    "description": "A parametric flange design",
                    "engine": "freecad",
                    "parameters": {"diameter": 100, "thickness": 10, "hole_diameter": 20},
                    "lastModified": "2024-01-14",
                    "created_at": "2024-01-01T00:00:00Z",
                    "status": ProjectStatus.COMPLETED.value,
                    "current_version": 1,
                    "ai_model_used": "Demo",
                    "messages": []
                }
            ]
            # Add demo projects to the beginning of the list
            formatted_projects = demo_projects + formatted_projects
        
        return formatted_projects
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get projects error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects"
        )


@router.get("/{project_id}/download/{format}")
async def download_project_file(
    project_id: str,
    format: str,
    version: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Generate a pre-signed URL for downloading a project output file."""
    try:
        user_id = current_user["id"]
        
        # Handle demo projects
        if project_id.startswith("demo-project-"):
            if user_id != "demo-user":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            # Demo projects don't have actual files
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demo projects use placeholder files. No actual model files available for download."
            )
        
        # Verify project belongs to user
        project = project_service.get_project_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Direct S3 project name mapping based on project ID
        # S3 structure: output/project-{shortId}/v1/project-{shortId}.{format}
        # Extract short ID from project metadata or use last 8 chars of project ID
        short_id = None
        if project.get("latest_s3_input") and isinstance(project["latest_s3_input"], dict):
            stored_name = project["latest_s3_input"].get("project_name", "")
            if stored_name.startswith("project-"):
                short_id = stored_name.replace("project-", "")
        
        if not short_id and len(project_id) >= 8:
            short_id = project_id[-8:]  # Use last 8 characters
        
        project_name_candidates = [
            f"project-{short_id}" if short_id else f"project-{project_id}",
            project_id  # Fallback to full ID
        ]
        logger.info(f"🔍 S3 mapping: project_id={project_id}, short_id={short_id}, candidates={project_name_candidates}")
        
        format_upper = format.upper()
        
        logger.info(f"🔄 Download request for project_id: {project_id}")
        logger.info(f"🔍 Project from DB: title='{project.get('title')}', name='{project.get('name')}'")
        logger.info(f"🔍 Will try S3 paths: {project_name_candidates}")
        logger.info(f"🔍 Looking for format: {format_upper}")
        
        # Try to find files using different project name strategies
        files = []
        successful_project_name = None
        
        for project_name in project_name_candidates:
            try:
                logger.info(f"🔍 Checking S3 for files under path: output/{project_name}/")
                files = await s3_service.check_output_files(project_name)
                logger.info(f"🔍 S3 returned {len(files)} files for '{project_name}': {[f.get('filename', 'unknown') for f in files]}")
                
                if files:
                    successful_project_name = project_name
                    logger.info(f"✅ Found files using project name: {project_name}")
                    break
                else:
                    logger.info(f"⚠️ No files found for project name: {project_name}")
            except Exception as e:
                logger.warning(f"❌ Error checking project name '{project_name}': {e}")
                continue
        
        if not files:
            logger.warning(f"No files found for project {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No output files found for project. The EC2 worker may still be processing your script."
            )
        
        # Find matching file
        matching_file = None
        for file in files:
            file_format = file.get("format", "").upper().lstrip('.')  # Remove leading dot
            if file_format == format_upper:
                if version is None or file.get("version") == version:
                    matching_file = file
                    break
        
        if not matching_file:
            available_formats = [f.get("format", "").upper().lstrip('.') for f in files]
            logger.warning(f"Format {format_upper} not found. Available: {available_formats}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Format {format_upper} not available. Available formats: {', '.join(available_formats)}"
            )
        
        # Generate pre-signed URL
        download_url = await s3_service.generate_download_url(
            project_name=successful_project_name,
            filename=matching_file["filename"],
            version=matching_file.get("version"),
            expiration=3600  # 1 hour
        )
        
        if not download_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate download URL"
            )
        
        logger.info(f"✅ Generated download URL for {matching_file['filename']}")
        
        return {
            "success": True,
            "download_url": download_url,
            "filename": matching_file["filename"],
            "format": format_upper,
            "version": matching_file.get("version"),
            "size": matching_file.get("size"),
            "last_modified": matching_file.get("last_modified")
        }
        
    except Exception as s3_error:
        logger.error(f"S3 service error: {s3_error}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No output files found for this project. The EC2 worker may still be processing your script."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download project file error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )


@router.get("/{project_id}/debug")
async def debug_project_files(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Debug endpoint to see what files exist for a project in S3."""
    try:
        user_id = current_user["id"]
        
        # Handle demo projects
        if project_id.startswith("demo-project-"):
            return {"message": "Demo projects don't have S3 files", "project_id": project_id}
        
        # Get project from database
        project = project_service.get_project_by_id(project_id)
        if not project:
            return {"error": "Project not found in database", "project_id": project_id}
        
        if project.get("user_id") != user_id:
            return {"error": "Access denied", "project_id": project_id}
        
        # Try different project name strategies based on S3 structure
        project_name_candidates = [
            f"project-{project_id}",  # Most likely format in S3
            project_id,  # Direct project ID
            project.get("title", project_id),  # Project title from database
            project.get("name", project_id),   # Project name from database
        ]
        
        # Also try shortened versions if the ID is long (ObjectId format)
        if len(project_id) == 24:  # MongoDB ObjectId length
            short_id = project_id[-8:]  # Last 8 characters
            project_name_candidates.extend([
                f"project-{short_id}",
                short_id
            ])
        
        debug_info = {
            "project_id": project_id,
            "project_from_db": {
                "title": project.get("title"),
                "name": project.get("name"),
                "user_id": project.get("user_id")
            },
            "s3_search_results": {},
            "all_projects_in_s3": []
        }
        
        # Check each project name candidate
        for project_name in project_name_candidates:
            try:
                files = await s3_service.check_output_files(project_name)
                debug_info["s3_search_results"][project_name] = {
                    "file_count": len(files),
                    "files": [{"filename": f.get("filename"), "format": f.get("format"), "version": f.get("version")} for f in files]
                }
            except Exception as e:
                debug_info["s3_search_results"][project_name] = {"error": str(e)}
        
        # Note: Removed S3 bucket scanning for security and performance reasons
        debug_info["note"] = "S3 bucket scanning disabled for security reasons"
        
        return debug_info
        
    except Exception as e:
        return {"error": str(e), "project_id": project_id}


@router.get("/{project_id}/chat")
async def get_project_chat(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get chat messages for a project."""
    try:
        user_id = current_user["id"]
        
        # Handle demo projects
        if project_id.startswith("demo-project-"):
            if user_id != "demo-user":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            # Return empty messages for demo projects
            return []
        
        # Verify project belongs to user
        project = project_service.get_project_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get messages for this project
        messages = project_service.get_project_messages(project_id)
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat messages"
        )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a project and all associated data."""
    try:
        user_id = current_user["id"]
        
        # Handle demo projects
        if project_id.startswith("demo-project-"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete demo projects"
            )
        
        # Verify project exists and belongs to user
        project = project_service.get_project_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete the project
        success = project_service.delete_project(project_id)
        
        if success:
            logger.info(f"✅ Successfully deleted project {project_id}")
            return {"success": True, "message": "Project deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )


@router.post("/")
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project."""
    try:
        user_id = current_user["id"]
        
        # Generate a proper S3 project name
        import uuid
        s3_project_name = f"project-{str(uuid.uuid4())[:8]}"
        
        # Create project using project service (new schema)
        project_dict = {
            "project_name": project_data.name,
            "user_id": user_id,
            "metadata": {
                "description": project_data.description,
                "engine": project_data.engine,
                "parameters": project_data.parameters
            },
            "latest_s3_input": {"project_name": s3_project_name}
        }
        project_id = project_service.create_project(project_dict)
        
        # Get created project
        created_project = project_service.get_project_by_id(project_id)
        
        # Format response
        project = {
            "id": project_id,
            "name": created_project["project_name"],
            "description": created_project["metadata"].get("description", ""),
            "engine": created_project["metadata"].get("engine", "freecad"),
            "parameters": created_project["metadata"].get("parameters", {}),
            "lastModified": created_project["updated_at"].isoformat() if isinstance(created_project["updated_at"], datetime) else created_project["updated_at"],
            "created_at": created_project["created_at"].isoformat() if isinstance(created_project["created_at"], datetime) else created_project["created_at"],
            "messages": []
        }
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project."""
    try:
        user_id = current_user["id"]
        
        # Get project from database using project service
        project = project_service.get_project_by_id(project_id)
        
        if not project or project["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Format response
        return {
            "id": project["project_id"],
            "name": project["project_name"],
            "description": project["metadata"].get("description", ""),
            "engine": project["metadata"].get("engine", "freecad"),
            "parameters": project["metadata"].get("parameters", {}),
            "lastModified": project["updated_at"].isoformat() if isinstance(project["updated_at"], datetime) else project["updated_at"],
            "created_at": project["created_at"].isoformat() if isinstance(project["created_at"], datetime) else project["created_at"],
            "messages": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project"
        )


@router.get("/{project_id}/chat")
async def get_chat_history(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (allow demo projects)
        if project_id.startswith("demo-project-"):
            # Demo projects are allowed for demo user
            if user_id != "demo-user":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            # Skip database lookup for demo projects
        else:
            project = project_service.get_project_by_id(project_id)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get chat history from database (skip for demo projects)
        if project_id.startswith("demo-project-"):
            messages = []  # Demo projects don't have database chat history
        else:
            try:
                messages = project_service.get_project_messages(project_id)
                if messages is None:
                    messages = []
            except Exception as e:
                logger.error(f"Failed to get project messages: {e}")
                messages = []
        
        # If no messages and this is a demo project, return sample messages
        if not messages and project_id.startswith("demo-project-"):
            if project_id == "demo-project-1":
                messages = [
                    {
                        "id": "demo-msg-1",
                        "role": "user",
                        "content": "Create a simple cube",
                        "timestamp": "2024-01-15T10:00:00Z"
                    },
                    {
                        "id": "demo-msg-2", 
                        "role": "assistant",
                        "content": "I'll create a parametric cube for you. Here's the generated code:\n\n```python\nimport cadquery as cq\n\n# Generate a cube\ncube = cq.Workplane(\"XY\").box(width, height, depth)\n\n# Show the result\nshow_object(cube)\n```",
                        "timestamp": "2024-01-15T10:01:00Z"
                    }
                ]
            elif project_id == "demo-project-2":
                messages = [
                    {
                        "id": "demo-msg-3",
                        "role": "user", 
                        "content": "Design a flange with bolt holes",
                        "timestamp": "2024-01-14T14:00:00Z"
                    },
                    {
                        "id": "demo-msg-4",
                        "role": "assistant",
                        "content": "I'll create a parametric flange design:\n\n```python\nimport cadquery as cq\n\n# Create flange with bolt holes\nflange = cq.Workplane(\"XY\").circle(diameter/2).extrude(thickness)\nflange = flange.faces(\">Z\").circle(hole_diameter/2).cutThruAll()\n\nshow_object(flange)\n```",
                        "timestamp": "2024-01-14T14:01:00Z"
                    }
                ]
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history"
        )


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update a project."""
    try:
        user_id = current_user["id"]
        
        # Don't allow updating demo projects
        if project_id.startswith("demo-project-"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update demo projects"
            )
        
        # Verify project ownership
        try:
            project = project_service.get_project_by_id(project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Check if project has user_id field (for database projects)
            if "user_id" in project and project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying project ownership: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while verifying project"
            )
        
        # Update project in database
        project_dict = {
            "project_name": project_data.name,
            "metadata": {
                "description": project_data.description,
                "engine": project_data.engine,
                "parameters": project_data.parameters
            }
        }
        
        # Update project in database with error handling
        try:
            success = project_service.update_project(project_id, project_dict)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update project in database"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while updating project"
            )
        
        # Get updated project
        try:
            updated_project = project_service.get_project_by_id(project_id)
            if not updated_project:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve updated project"
                )
        except Exception as e:
            logger.error(f"Error retrieving updated project: {e}")
            # Return a basic response if we can't get the updated project
            return {
                "id": project_id,
                "name": project_data.name,
                "description": project_data.description,
                "engine": project_data.engine,
                "parameters": project_data.parameters,
                "lastModified": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
        
        # Format response
        return {
            "id": project_id,
            "name": updated_project["project_name"],
            "description": updated_project["metadata"].get("description", ""),
            "engine": updated_project["metadata"].get("engine", "freecad"),
            "parameters": updated_project["metadata"].get("parameters", {}),
            "lastModified": updated_project["updated_at"].isoformat() if isinstance(updated_project["updated_at"], datetime) else updated_project["updated_at"],
            "created_at": updated_project["created_at"].isoformat() if isinstance(updated_project["created_at"], datetime) else updated_project["created_at"],
            "messages": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a project."""
    try:
        user_id = current_user["id"]
        
        # Don't allow deleting demo projects
        if project_id.startswith("demo-project-"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete demo projects"
            )
        
        # Verify project ownership
        project = project_service.get_project_by_id(project_id)
        if not project or project["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Delete project from database
        project_service.delete_project(project_id)
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )


@router.post("/{project_id}/chat")
async def send_chat_message(
    project_id: str,
    message_data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Send a chat message for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership
        project = project_service.get_project_by_id(project_id)
        if not project or project["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Save user message
        user_msg_data = {
            "project_id": project_id,
            "user_id": user_id,
            "role": "user",
            "content": message_data.message,
            "metadata": message_data.context or {}
        }
        db_service.create_chat_message(user_msg_data)
        
        # Generate AI response
        import uuid
        response_id = f"msg-{str(uuid.uuid4())[:8]}"
        # Simple AI response logic (can be enhanced with actual AI service)
        user_message = message_data.message.lower()
        if "cube" in user_message:
            ai_response = "I'll create a cube for you. Here's the generated CadQuery code:\n\n```python\nimport cadquery as cq\n\n# Generate a cube\ncube = cq.Workplane(\"XY\").box(10, 10, 10)\n\n# Show the result\nshow_object(cube)\n```"
        elif "cylinder" in user_message:
            ai_response = "I'll create a cylinder for you. Here's the generated CadQuery code:\n\n```python\nimport cadquery as cq\n\n# Generate a cylinder\ncylinder = cq.Workplane(\"XY\").circle(5).extrude(10)\n\n# Show the result\nshow_object(cylinder)\n```"
        else:
            ai_response = f"I understand you want to: {message_data.message}. I'll help you create that design. Here's some generated code:\n\n```python\nimport cadquery as cq\n\n# Generate based on your request\nresult = cq.Workplane(\"XY\").box(10, 10, 10)\n\n# Show the result\nshow_object(result)\n```"
        
        # Save AI response
        ai_msg_data = {
            "project_id": project_id,
            "user_id": user_id,
            "role": "assistant",
            "content": ai_response,
            "metadata": {}
        }
        db_service.create_chat_message(ai_msg_data)
        
        response = {
            "id": response_id,
            "role": "assistant",
            "content": ai_response,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send chat message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send chat message"
        )

