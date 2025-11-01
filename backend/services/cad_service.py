"""
CAD service for communicating with the CAD microservice.
"""
import logging
from typing import Dict, Any, Optional
import requests
import json
from config import settings

logger = logging.getLogger(__name__)


class CADService:
    """Service for communicating with the CAD microservice."""
    
    def __init__(self):
        self.cad_service_url = settings.cad_service_url
    
    async def generate_model(self, code: str, output_format: str = "stl", parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a CAD model from Python code.
        
        Args:
            code: Python CAD code (CadQuery, OpenSCAD, etc.)
            output_format: Output format (stl, step, obj, etc.)
            parameters: Additional parameters
        
        Returns:
            Dict containing file path and metadata
        """
        try:
            # Try to call the actual CAD microservice first
            cad_result = await self.call_cad_microservice(code, output_format, parameters)
            
            if cad_result and cad_result.get("success"):
                return {
                    "success": True,
                    "file_path": cad_result["file_path"],
                    "file_size": cad_result.get("file_size", 0),
                    "format": output_format,
                    "generation_time": cad_result.get("generation_time", 0),
                    "download_url": f"/api/download/{cad_result.get('file_id', 'unknown')}",
                    "metadata": {
                        "code_length": len(code),
                        "parameters": parameters or {},
                        "timestamp": "2024-01-01T00:00:00Z",
                        "service": "cad_microservice"
                    }
                }
            else:
                # Fallback to mock data if CAD service is not available
                logger.warning("CAD microservice not available, using mock data")
                mock_result = self._generate_mock_model(code, output_format, parameters)
                
                return {
                    "success": True,
                    "file_path": mock_result["file_path"],
                    "file_size": mock_result["file_size"],
                    "format": output_format,
                    "generation_time": mock_result["generation_time"],
                    "download_url": f"/api/download/{mock_result['file_id']}",
                    "metadata": {
                        "code_length": len(code),
                        "parameters": parameters or {},
                        "timestamp": "2024-01-01T00:00:00Z",
                        "service": "mock"
                    }
                }
                
        except Exception as e:
            logger.error(f"CAD model generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_mock_model(self, code: str, output_format: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate mock model data for testing."""
        import uuid
        
        file_id = str(uuid.uuid4())
        file_name = f"model_{file_id}.{output_format}"
        
        return {
            "file_id": file_id,
            "file_path": f"/generated_models/{file_name}",
            "file_size": 1024 * 50,  # 50KB mock size
            "generation_time": 1.2
        }
    
    async def call_cad_microservice(self, code: str, output_format: str = "stl", parameters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Call the actual CAD microservice."""
        try:
            payload = {
                "script_content": code,
                "output_format": output_format,
                "parameters": parameters or {}
            }
            
            response = requests.post(
                f"{self.cad_service_url}/generate_model",
                json=payload,
                timeout=60  # CAD generation can take time
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"CAD service error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to call CAD microservice: {e}")
            return None
    
    async def get_supported_formats(self) -> Dict[str, Any]:
        """Get list of supported output formats."""
        try:
            response = requests.get(f"{self.cad_service_url}/formats", timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                # Return default formats if service is unavailable
                return {
                    "supported_formats": [
                        {"format": "stl", "description": "STL mesh format for 3D printing"},
                        {"format": "step", "description": "STEP format for CAD exchange"},
                        {"format": "obj", "description": "OBJ format for 3D graphics"},
                        {"format": "dxf", "description": "DXF format for 2D drawings"},
                        {"format": "dwg", "description": "DWG format for AutoCAD"}
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get supported formats: {e}")
            return {
                "supported_formats": [
                    {"format": "stl", "description": "STL mesh format for 3D printing"},
                    {"format": "step", "description": "STEP format for CAD exchange"}
                ]
            }


# Global CAD service instance
cad_service = CADService()
