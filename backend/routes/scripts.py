"""
Script management routes for S3-based CAD script handling.
Handles versioning, uploads, downloads, and output file management.
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
import logging
from pydantic import BaseModel
import asyncio
from datetime import datetime, timezone

from services.database import db_service
from services.project_service import project_service
from services.s3_service import s3_service
from dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["scripts"])
security = HTTPBearer()


@router.get("/test")
async def test_route():
    """Simple test endpoint to verify routing works."""
    return {"success": True, "message": "Scripts router is working", "route": "/api/projects/test"}


@router.get("/{project_name}/debug")
async def debug_project_files(
    project_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Debug endpoint to check S3 files and project status."""
    try:
        user_id = current_user["id"]
        
        # Get project info
        project = project_service.get_project_by_id(project_name)
        if not project:
            project = db_service.get_project(project_name)
        
        # Get all output files
        output_files = await s3_service.check_output_files(project_name)
        
        # Extract version info
        versions = list(set(f.get("version") for f in output_files if f.get("version")))
        versions.sort(reverse=True)  # Latest first
        latest_version = versions[0] if versions else None
        
        # Group files by format
        formats_by_version = {}
        for file in output_files:
            version = file.get("version", "unknown")
            if version not in formats_by_version:
                formats_by_version[version] = []
            formats_by_version[version].append(file["format"])
        
        return {
            "success": True,
            "project_name": project_name,
            "project_found": bool(project),
            "project_owner": project.get("created_by") if project else None,
            "user_id": user_id,
            "access_allowed": project.get("created_by") == user_id if project else False,
            "output_files_count": len(output_files),
            "output_files": output_files,
            "s3_configured": bool(s3_service.s3_client and s3_service.aws_bucket_name),
            "versions_available": versions,
            "latest_version": latest_version,
            "formats_by_version": formats_by_version,
            "stl_available": any(f["format"].upper() == ".STL" for f in output_files),
            "obj_available": any(f["format"].upper() == ".OBJ" for f in output_files)
        }
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_name": project_name
        }


class ScriptUploadRequest(BaseModel):
    """Request model for script upload."""
    project_name: str
    code: str
    metadata: Optional[Dict[str, Any]] = {}


class ScriptResponse(BaseModel):
    """Response model for script operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/{project_name}/scripts")
async def list_project_scripts(
    project_name: str,
    current_user: dict = Depends(get_current_user)
):
    """List all script versions for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get scripts from S3
        scripts = await s3_service.list_project_scripts(project_name)
        
        return {
            "success": True,
            "project_name": project_name,
            "scripts": scripts,
            "total_versions": len(scripts)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List scripts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list project scripts"
        )


@router.get("/{project_name}/script/{version}")
async def get_script_content(
    project_name: str,
    version: int,
    current_user: dict = Depends(get_current_user)
):
    """Get the content of a specific script version."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get script content from S3
        content = await s3_service.get_script_content(project_name, version)
        
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script version {version} not found"
            )
        
        return {
            "success": True,
            "project_name": project_name,
            "version": version,
            "content": content,
            "content_type": "text/x-python"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get script content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get script content"
        )


@router.post("/{project_name}/upload-script")
async def upload_script(
    project_name: str,
    request: ScriptUploadRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Upload a new script version to S3 with automatic versioning."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Upload script to S3 with versioning
        upload_result = await s3_service.upload_script(
            code=request.code,
            project_name=project_name,
            user_id=user_id
        )
        
        if not upload_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload script: {upload_result.get('error', 'Unknown error')}"
            )
        
        # Update project metadata in database
        if not project_name.startswith("demo-project-"):
            try:
                project_update = {
                    "metadata.latest_script_version": upload_result["version"],
                    "metadata.latest_script_s3_path": upload_result["s3_path"],
                    "metadata.script_upload_time": upload_result["upload_time"]
                }
                db_service.update_project(project_name, project_update)
            except Exception as e:
                logger.warning(f"Failed to update project metadata: {e}")
        
        # Start background task to poll for output files
        background_tasks.add_task(
            poll_for_output_files,
            project_name,
            upload_result["version"],
            user_id
        )
        
        return {
            "success": True,
            "message": "Script uploaded successfully",
            "data": {
                "project_name": project_name,
                "version": upload_result["version"],
                "s3_path": upload_result["s3_path"],
                "upload_time": upload_result["upload_time"],
                "status": "uploaded",
                "next_step": "freecad_processing"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload script error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload script"
        )


@router.get("/{project_name}/outputs")
async def get_project_outputs(
    project_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get available output files for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            # Try to get project by ID first (frontend sends project ID)
            project = project_service.get_project_by_id(project_name)
            if not project:
                # Fallback: try by name for backward compatibility
                project = db_service.get_project(project_name)
            
            if not project:
                logger.warning(f"Project not found: {project_name}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            project_owner = project.get("created_by")
            # Handle projects with null owners (legacy projects)
            if project_owner is None:
                logger.warning(f"Project {project_name} has null owner, allowing access for user {user_id}")
            elif project_owner != user_id:
                logger.warning(f"Project access denied for user {user_id}, project owned by {project_owner}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or access denied"
                )
        
        # Get output files from S3
        logger.info(f"Checking output files for project {project_name} (outputs endpoint)")
        output_files = await s3_service.check_output_files(project_name)
        logger.info(f"Found {len(output_files)} output files: {[f['filename'] for f in output_files]}")
        
        return {
            "success": True,
            "project_name": project_name,
            "output_files": output_files,
            "total_files": len(output_files),
            "available_formats": list(set(f["format"] for f in output_files))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project outputs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project outputs"
        )


@router.get("/{project_name}/download/{format}")
async def download_output_file(
    project_name: str,
    format: str,
    version: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Generate a pre-signed URL for downloading an output file from versioned folders."""
    import time
    start_time = time.time()
    logger.info(f"🔄 Download request started for {project_name}/{format}")
    
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            # Try to get project by ID first (frontend sends project ID)
            logger.info(f"Looking up project by ID: {project_name}")
            project = project_service.get_project_by_id(project_name)
            if not project:
                # Fallback: try by name for backward compatibility
                logger.info(f"Project not found by ID, trying by name: {project_name}")
                project = db_service.get_project(project_name)
            
            if not project:
                logger.warning(f"Project not found: {project_name}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            project_owner = project.get("created_by")
            logger.info(f"Project {project_name} owner: {project_owner}, requesting user: {user_id}")
            
            # Handle projects with null owners (legacy projects or data migration issues)
            if project_owner is None:
                logger.warning(f"Project {project_name} has null owner, allowing access for user {user_id}")
                # Allow access for projects with null owners - they may be legacy projects
            elif project_owner != user_id:
                logger.warning(f"Project access denied for user {user_id}, project owned by {project_owner}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or access denied"
                )
        
        # Validate format
        supported_formats = ['.FCSTD', '.STL', '.STEP', '.OBJ', '.GLTF']
        format_upper = format.upper()
        if not format_upper.startswith('.'):
            format_upper = '.' + format_upper
        
        if format_upper not in supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format. Supported formats: {supported_formats}"
            )
        
        # Find the output file with matching format
        logger.info(f"Checking output files for project {project_name}, format {format_upper}")
        output_files = await s3_service.check_output_files(project_name, version)
        logger.info(f"Found {len(output_files)} output files: {[f['filename'] for f in output_files]}")
        
        matching_file = None
        
        # First, try to find exact format match
        for file in output_files:
            if file["format"].upper() == format_upper:
                matching_file = file
                break
        
        # If STL not found, try OBJ as fallback (both work in Three.js)
        if not matching_file and format_upper == '.STL':
            logger.info("STL not found, trying OBJ as fallback")
            for file in output_files:
                if file["format"].upper() == '.OBJ':
                    matching_file = file
                    logger.info(f"Using OBJ fallback: {file['filename']}")
                    break
        
        if not matching_file:
            version_text = f" version {version}" if version else ""
            logger.warning(f"No {format_upper} file found for project {project_name}{version_text}")
            logger.warning(f"Available formats: {[f['format'] for f in output_files]}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {format_upper} file found for project {project_name}{version_text}. Available: {[f['format'] for f in output_files]}"
            )
        
        # Generate pre-signed URL with version support
        logger.info(f"Generating pre-signed URL for {matching_file['filename']} v{matching_file.get('version')}")
        download_url = await s3_service.generate_download_url(
            project_name=project_name,
            filename=matching_file["filename"],
            version=matching_file.get("version"),
            expiration=3600  # 1 hour
        )
        
        if not download_url:
            logger.error(f"Failed to generate pre-signed URL for {matching_file['filename']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate download URL"
            )
        
        logger.info(f"Successfully generated pre-signed URL for {matching_file['filename']}")
        
        # Log completion time
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Download request completed in {elapsed_time:.2f}s for {project_name}/{format}")
        
        return {
            "success": True,
            "download_url": download_url,
            "filename": matching_file["filename"],
            "format": format_upper,
            "version": matching_file.get("version"),
            "size": matching_file["size"],
            "expires_in": 3600,
            "processing_time_seconds": round(elapsed_time, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download output file error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )


@router.post("/auto-fix-error")
async def auto_fix_script_error(request_body: dict):
    """
    Auto-fix a failed script by replacing it with corrected FreeCAD version.
    This endpoint is called by the EC2 worker when it encounters errors.
    No authentication required for EC2 worker calls.
    """
    try:
        project_name = request_body.get("project_name")
        version = request_body.get("version")
        error_message = request_body.get("error_message", "Unknown error")
        log_file = request_body.get("log_file")  # Optional log file name
        
        if not project_name or version is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="project_name and version are required"
            )
        
        # Auto-fix the failed script using log analysis and AI
        success = await s3_service.auto_fix_failed_script(
            project_name=project_name,
            version=version,
            error_message=error_message,
            log_file=log_file
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to auto-fix script"
            )
        
        return {
            "success": True,
            "project_name": project_name,
            "version": version,
            "message": "Script auto-fixed with FreeCAD replacement. EC2 worker can reprocess.",
            "action": "script_replaced"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-fix script error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to auto-fix script"
        )


@router.post("/debug-auto-fix")
async def debug_auto_fix(request_body: dict):
    """
    Debug endpoint to manually trigger auto-fix for testing.
    """
    try:
        project_name = request_body.get("project_name")
        version = request_body.get("version", 1)
        
        if not project_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="project_name is required"
            )
        
        # Get recent logs for the project
        logs = await s3_service.get_project_logs(project_name, limit=5)
        
        # Try to auto-fix with latest error
        success = await s3_service.auto_fix_failed_script(
            project_name=project_name,
            version=version,
            error_message="Debug auto-fix test",
            log_file=logs[0]["filename"] if logs else None
        )
        
        return {
            "success": success,
            "message": f"Debug auto-fix {'succeeded' if success else 'failed'} for {project_name} v{version}",
            "logs_found": len(logs),
            "latest_log": logs[0]["filename"] if logs else None
        }
        
    except Exception as e:
        logger.error(f"Error in debug auto-fix: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug auto-fix failed: {str(e)}"
        )


@router.get("/{project_name}/errors")
async def get_project_errors(
    project_name: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get recent error logs for a project."""
    """Get recent log files for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get log files from S3
        log_files = await s3_service.get_project_logs(project_name, limit)
        
        return {
            "success": True,
            "project_name": project_name,
            "log_files": log_files,
            "total_files": len(log_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project logs"
        )


@router.get("/{project_name}/logs/{log_filename}")
async def get_log_content(
    project_name: str,
    log_filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the content of a specific log file."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get log content from S3
        content = await s3_service.get_log_content(project_name, log_filename)
        
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log file not found"
            )
        
        return {
            "success": True,
            "project_name": project_name,
            "log_filename": log_filename,
            "content": content,
            "content_type": "text/plain"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get log content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get log content"
        )


@router.get("/{project_name}/formats/{version}")
async def get_available_formats(
    project_name: str,
    version: int,
    current_user: dict = Depends(get_current_user)
):
    """Get all available export formats for a specific version."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get output files for this version
        output_files = await s3_service.check_output_files(project_name, version)
        
        if not output_files:
            return {
                "success": True,
                "project_name": project_name,
                "version": version,
                "available_formats": [],
                "files": [],
                "message": "No output files available for this version"
            }
        
        # Extract available formats and file info
        formats = {}
        for file in output_files:
            format_type = file["format"]
            formats[format_type] = {
                "filename": file["filename"],
                "size": file["size"],
                "last_modified": file["last_modified"],
                "download_available": True
            }
        
        return {
            "success": True,
            "project_name": project_name,
            "version": version,
            "available_formats": list(formats.keys()),
            "files": formats,
            "total_files": len(output_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get available formats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available formats"
        )


@router.get("/{project_name}/metadata/{version}")
async def get_version_metadata(
    project_name: str,
    version: int,
    current_user: dict = Depends(get_current_user)
):
    """Get metadata.json for a specific version."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get version metadata
        metadata = await s3_service.get_version_metadata(project_name, version)
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata not found for {project_name} version {version}"
            )
        
        return {
            "success": True,
            "project_name": project_name,
            "version": version,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get version metadata error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get version metadata"
        )


@router.get("/{project_name}/status")
async def get_project_status(
    project_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the current processing status of a project with version correlation."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get latest script version and check status
        scripts = await s3_service.list_project_scripts(project_name)
        
        if not scripts:
            status_info = {
                "status": "no_scripts",
                "message": "No scripts uploaded yet",
                "latest_version": None,
                "output_files_available": False
            }
            return {
                "success": True,
                "project_name": project_name,
                "status_info": status_info,
                "script_count": 0,
                "output_file_count": 0
            }
        
        latest_script = scripts[0]  # Scripts are sorted by version (descending)
        latest_version = latest_script["version"]
        
        # Check for output files in the latest version folder
        output_files = await s3_service.check_output_files(project_name, latest_version)
        
        # Get metadata if available
        metadata = await s3_service.get_version_metadata(project_name, latest_version)
        
        if output_files:
            status_info = {
                "status": "completed",
                "message": "Model files are ready for download",
                "latest_version": latest_version,
                "output_files_available": True,
                "available_formats": list(set(f["format"] for f in output_files)),
                "processing_time": metadata.get("processing_time") if metadata else None,
                "worker_id": metadata.get("worker_id") if metadata else None
            }
        else:
            status_info = {
                "status": "processing",
                "message": "FreeCAD is processing the script",
                "latest_version": latest_version,
                "output_files_available": False
            }
        
        return {
            "success": True,
            "project_name": project_name,
            "status_info": status_info,
            "script_count": len(scripts),
            "output_file_count": len(output_files),
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project status"
        )


async def poll_for_output_files(project_name: str, version: int, user_id: str):
    """
    Background task to poll for output files after script upload.
    Now checks for versioned output folders and creates metadata.
    Checks every 30 seconds for up to 10 minutes.
    """
    max_attempts = 20  # 10 minutes with 30-second intervals
    attempt = 0
    start_time = datetime.now(timezone.utc)
    
    logger.info(f"Starting output polling for {project_name} v{version}")
    
    while attempt < max_attempts:
        try:
            # Wait before checking
            await asyncio.sleep(30)
            attempt += 1
            
            # Check for output files in the specific version folder
            output_files = await s3_service.check_output_files(project_name, version)
            
            if output_files:
                # Calculate processing time
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                
                # Extract filenames for metadata
                output_filenames = [f["filename"] for f in output_files]
                
                # Generate log filename (expected pattern)
                timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                expected_log_file = f"{project_name}_info_{timestamp_str}.log"
                
                # Mark script as processed with enhanced metadata
                await s3_service.mark_script_processed(
                    project_name=project_name,
                    version=version,
                    output_files=output_filenames,
                    processing_time=processing_time,
                    worker_id="aws-freecad-worker",
                    log_file=expected_log_file
                )
                
                # Update project status in database
                try:
                    project_update = {
                        "metadata.processing_status": "completed",
                        "metadata.output_files_ready": True,
                        "metadata.completion_time": datetime.now(timezone.utc).isoformat(),
                        "metadata.latest_version": version,
                        "metadata.output_files_count": len(output_filenames),
                        "metadata.processing_time": processing_time
                    }
                    db_service.update_project(project_name, project_update)
                except Exception as e:
                    logger.warning(f"Failed to update project status: {e}")
                
                logger.info(f"✅ Output files ready for {project_name} v{version} ({len(output_filenames)} files)")
                break
            
            logger.info(f"Polling attempt {attempt}/{max_attempts} for {project_name} v{version}")
            
        except Exception as e:
            logger.error(f"Error in output polling: {e}")
            continue
    
    if attempt >= max_attempts:
        logger.warning(f"⚠️ Output polling timeout for {project_name} v{version}")
        
        # Mark as processed with timeout status
        await s3_service.mark_script_processed(
            project_name=project_name,
            version=version,
            output_files=[],
            processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
            worker_id="timeout",
            log_file=None
        )
        
        # Update project status to indicate timeout
        try:
            project_update = {
                "metadata.processing_status": "timeout",
                "metadata.output_files_ready": False,
                "metadata.timeout_time": datetime.now(timezone.utc).isoformat(),
                "metadata.timeout_version": version
            }
            db_service.update_project(project_name, project_update)
        except Exception as e:
            logger.warning(f"Failed to update project timeout status: {e}")


@router.get("/{project_name}/errors")
async def get_project_errors(
    project_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get error information for a project."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get failed scripts for this project
        failed_scripts = await s3_service.get_failed_scripts(project_name)
        
        return {
            "success": True,
            "project_name": project_name,
            "failed_scripts": failed_scripts,
            "total_errors": len(failed_scripts)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project errors error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project errors"
        )


@router.post("/{project_name}/replace/{version}")
async def replace_failed_script(
    project_name: str,
    version: int,
    request_body: dict,
    current_user: dict = Depends(get_current_user)
):
    """Replace a failed script with corrected code."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get the new code from request body
        new_code = request_body.get("code")
        if not new_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code is required"
            )
        
        # Replace the failed script
        result = await s3_service.replace_failed_script(
            project_name=project_name,
            version=version,
            new_code=new_code,
            user_id=user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to replace script")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Replace failed script error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to replace script"
        )


@router.post("/{project_name}/retry/{version}")
async def retry_failed_script(
    project_name: str,
    version: int,
    current_user: dict = Depends(get_current_user)
):
    """Retry processing a failed script."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Retry the failed script
        result = await s3_service.retry_failed_script(
            project_name=project_name,
            version=version
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to retry script")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retry failed script error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry script"
        )


@router.post("/{project_name}/mark-failed/{version}")
async def mark_script_failed(
    project_name: str,
    version: int,
    request_body: dict,
    current_user: dict = Depends(get_current_user)
):
    """Mark a script as failed (for testing/admin purposes)."""
    try:
        user_id = current_user["id"]
        
        # Verify project ownership (skip for demo projects)
        if not project_name.startswith("demo-project-"):
            project = db_service.get_project(project_name)
            if not project or project["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        # Get error message from request body
        error_message = request_body.get("error_message", "Manual failure marking")
        retry_count = request_body.get("retry_count", 0)
        
        # Mark script as failed
        success = await s3_service.mark_script_failed(
            project_name=project_name,
            version=version,
            error_message=error_message,
            retry_count=retry_count
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark script as failed"
            )
        
        return {
            "success": True,
            "project_name": project_name,
            "version": version,
            "message": "Script marked as failed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark script failed error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark script as failed"
        )
