"""
Monitoring and health check routes for S3 and AI services.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import logging
from datetime import datetime, timezone

from services.s3_service import s3_service
from services.ai_service import ai_service
from services.database import db_service
from services.config_validator import config_validator
from dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])
security = HTTPBearer()


@router.get("/health")
async def health_check():
    """Comprehensive health check for all services."""
    try:
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "services": {}
        }
        
        # Check S3 service
        try:
            s3_metrics = s3_service.get_performance_metrics()
            s3_configured = s3_metrics.get("configured", False)
            
            health_status["services"]["s3"] = {
                "status": "healthy" if s3_configured else "not_configured",
                "configured": s3_configured,
                "bucket": s3_metrics.get("bucket_name"),
                "region": s3_metrics.get("region"),
                "metrics": s3_metrics.get("s3_operations", {})
            }
        except Exception as e:
            health_status["services"]["s3"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check AI service
        try:
            ai_metrics = ai_service.get_performance_metrics()
            
            health_status["services"]["ai"] = {
                "status": "healthy",
                "metrics": ai_metrics
            }
        except Exception as e:
            health_status["services"]["ai"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check database service
        try:
            db_connected = db_service.client is not None
            if db_connected:
                db_service.client.admin.command('ping')
                db_status = "healthy"
            else:
                db_status = "not_connected"
            
            health_status["services"]["database"] = {
                "status": db_status,
                "connected": db_connected
            }
        except Exception as e:
            health_status["services"]["database"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/s3/status")
async def s3_status(current_user: dict = Depends(get_current_user)):
    """Get detailed S3 service status and metrics."""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        metrics = s3_service.get_performance_metrics()
        
        # Test S3 connectivity
        connectivity_test = {
            "can_connect": False,
            "can_list_objects": False,
            "error": None
        }
        
        try:
            if s3_service.s3_client and s3_service.aws_bucket_name:
                # Test basic connectivity
                s3_service.s3_client.head_bucket(Bucket=s3_service.aws_bucket_name)
                connectivity_test["can_connect"] = True
                
                # Test list objects
                s3_service.s3_client.list_objects_v2(
                    Bucket=s3_service.aws_bucket_name,
                    MaxKeys=1
                )
                connectivity_test["can_list_objects"] = True
                
        except Exception as e:
            connectivity_test["error"] = str(e)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "bucket_name": metrics.get("bucket_name"),
                "region": metrics.get("region"),
                "configured": metrics.get("configured")
            },
            "connectivity": connectivity_test,
            "performance_metrics": metrics.get("s3_operations", {}),
            "bucket_structure": {
                "input_prefix": "input/{project_name}/{project_name}_v{version}.py",
                "output_prefix": "output/{project_name}/v{version}/MyHeadlessModel.{format}",
                "metadata_prefix": "output/{project_name}/v{version}/metadata.json",
                "logs_prefix": "logs/{project_name}/{project_name}_info_{timestamp}.log",
                "processed_prefix": "processed/{project_name}/{project_name}_v{version}.py.done",
                "supported_formats": [".FCStd", ".STL", ".STEP", ".OBJ", ".GLTF"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"S3 status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get S3 status"
        )


@router.get("/ai/metrics")
async def ai_metrics(current_user: dict = Depends(get_current_user)):
    """Get AI service performance metrics."""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        metrics = ai_service.get_performance_metrics()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "performance_metrics": metrics,
            "service_status": {
                "gemini_configured": ai_service.gemini_client is not None,
                "openrouter_configured": ai_service.openrouter_client is not None,
                "s3_configured": ai_service.s3_client is not None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI metrics"
        )


@router.get("/system/info")
async def system_info(current_user: dict = Depends(get_current_user)):
    """Get system information and configuration status."""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        from config.settings import settings
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "environment": {
                "debug": settings.debug,
                "cors_origins": settings.cors_origins_list,
                "cad_service_url": settings.cad_service_url
            },
            "services_configured": {
                "mongodb": bool(settings.mongodb_uri),
                "gemini": bool(settings.gemini_api_key),
                "openrouter": bool(settings.openrouter_api_key),
                "aws_s3": all([
                    settings.aws_access_key_id,
                    settings.aws_secret_access_key,
                    settings.aws_bucket_name
                ])
            },
            "aws_config": {
                "bucket_name": settings.aws_bucket_name,
                "region": settings.aws_region,
                "credentials_configured": bool(settings.aws_access_key_id and settings.aws_secret_access_key)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system info"
        )


@router.post("/test/s3-upload")
async def test_s3_upload(current_user: dict = Depends(get_current_user)):
    """Test S3 upload functionality with a sample script."""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Test script content
        test_script = """import cadquery as cq

# Test cube for S3 upload verification
result = (
    cq.Workplane("XY")
    .box(10, 10, 10)
)

show_object(result)"""
        
        # Upload test script
        upload_result = await s3_service.upload_script(
            code=test_script,
            project_name="test-upload",
            user_id=current_user["id"]
        )
        
        if upload_result["success"]:
            return {
                "success": True,
                "message": "S3 upload test successful",
                "result": upload_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "message": "S3 upload test failed",
                "error": upload_result.get("error"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"S3 upload test error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 upload test failed"
        )


@router.get("/projects/{project_name}/processing-status")
async def get_processing_status(
    project_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed processing status for a project including S3 file states."""
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
        
        # Get comprehensive status from all S3 directories
        scripts = await s3_service.list_project_scripts(project_name)
        log_files = await s3_service.get_project_logs(project_name, limit=5)
        
        # Check for processed markers
        processed_scripts = []
        if s3_service.s3_client and s3_service.aws_bucket_name:
            try:
                response = s3_service.s3_client.list_objects_v2(
                    Bucket=s3_service.aws_bucket_name,
                    Prefix=f"processed/{project_name}/"
                )
                if 'Contents' in response:
                    for obj in response['Contents']:
                        if obj['Key'].endswith('.py.done'):
                            processed_scripts.append({
                                "key": obj['Key'],
                                "processed_at": obj['LastModified'].isoformat()
                            })
            except Exception as e:
                logger.warning(f"Error checking processed scripts: {e}")
        
        # Get version-specific information
        version_details = []
        latest_version = None
        total_output_files = 0
        
        if scripts:
            latest_version = scripts[0]["version"]  # Scripts are sorted by version (descending)
            
            # Check each version for outputs and metadata
            for script in scripts[:5]:  # Check last 5 versions
                version = script["version"]
                version_output_files = await s3_service.check_output_files(project_name, version)
                version_metadata = await s3_service.get_version_metadata(project_name, version)
                
                version_details.append({
                    "version": version,
                    "script_uploaded": script["last_modified"],
                    "output_files_count": len(version_output_files),
                    "output_files": version_output_files,
                    "metadata": version_metadata,
                    "has_metadata": version_metadata is not None
                })
                
                total_output_files += len(version_output_files)
        
        # Determine overall status based on latest version
        if not scripts:
            overall_status = "no_scripts"
            status_message = "No scripts have been uploaded yet"
        elif version_details and version_details[0]["output_files_count"] > 0:
            overall_status = "completed"
            status_message = f"Processing complete - {version_details[0]['output_files_count']} output files available for latest version"
        elif processed_scripts:
            overall_status = "processed_no_output"
            status_message = "Script processed but no output files found"
        else:
            overall_status = "processing"
            status_message = "Script uploaded, waiting for FreeCAD processing"
        
        return {
            "success": True,
            "project_name": project_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": overall_status,
            "status_message": status_message,
            "details": {
                "scripts": {
                    "count": len(scripts),
                    "latest_version": latest_version,
                    "versions": [s["version"] for s in scripts]
                },
                "output_files": {
                    "total_count": total_output_files,
                    "latest_version_count": version_details[0]["output_files_count"] if version_details else 0
                },
                "processed_scripts": {
                    "count": len(processed_scripts),
                    "scripts": processed_scripts
                },
                "logs": {
                    "count": len(log_files),
                    "latest": log_files[0] if log_files else None
                },
                "version_details": version_details
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get processing status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get processing status"
        )


@router.get("/config/validate")
async def validate_configuration(current_user: dict = Depends(get_current_user)):
    """Validate system configuration and connectivity."""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        validation_results = config_validator.validate_all()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "validation_results": validation_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate configuration"
        )


@router.get("/config/summary")
async def configuration_summary(current_user: dict = Depends(get_current_user)):
    """Get configuration summary showing what's configured."""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        summary = config_validator.get_configuration_summary()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configuration_summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get configuration summary"
        )
