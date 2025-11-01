from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import subprocess
import tempfile
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

app = FastAPI(title="CADSCRIBE CAD Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CADScript(BaseModel):
    script_content: str
    output_format: str = "stl"  # stl, step, obj, etc.
    parameters: Dict[str, Any] = {}

class ModelGenerationResponse(BaseModel):
    success: bool
    file_path: str
    file_size: int = Field(description="Size of the generated file in bytes")
    format: str = Field(description="Format of the generated file")
    message: str
    generation_time: float

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "cadscribe-cad-service",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/generate_model", response_model=ModelGenerationResponse)
async def generate_model(cad_script: CADScript):
    """
    Generate a CAD model from Python script using FreeCAD
    
    This endpoint accepts a Python CAD script and runs it through FreeCAD
    to generate the specified model format.
    """
    start_time = datetime.now(timezone.utc)
    script_path = None  # Track file for cleanup
    
    try:
        # Validate script content
        if not cad_script.script_content or "import" not in cad_script.script_content:
            raise HTTPException(status_code=400, detail="Invalid CAD script content")
        
        # Create temporary directory for this generation
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Write the script to a temporary file
                script_path = os.path.join(temp_dir, "model_script.py")
                with open(script_path, "w") as f:
                    f.write(cad_script.script_content)
                
                # Generate output filename with random ID
                file_id = str(uuid.uuid4())
                output_filename = f"model_{file_id}.{cad_script.output_format}"
                output_path = os.path.join(temp_dir, output_filename)
                
                # Run FreeCAD with the script
                freecad_cmd = ["freecad", "-c", script_path]
                try:
                    subprocess.run(
                        freecad_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,  # Increase timeout for complex models
                        check=True  # Raise on non-zero exit
                    )
                except subprocess.TimeoutExpired:
                    raise HTTPException(status_code=500, detail="CAD generation timed out")
                except subprocess.CalledProcessError as e:
                    raise HTTPException(status_code=500, detail=f"FreeCAD error: {e.stderr}")
                
                # Move generated file to final location
                os.makedirs("generated_models", exist_ok=True)
                final_path = os.path.join("generated_models", output_filename)
                
                if os.path.exists(output_path):
                    os.rename(output_path, final_path)
                    file_size = os.path.getsize(final_path)
                    generation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                    
                    return ModelGenerationResponse(
                        success=True,
                        file_path=final_path,
                        file_size=file_size,
                        format=cad_script.output_format,
                        message=f"Model generated successfully in {cad_script.output_format.upper()} format",
                        generation_time=generation_time
                    )
                else:
                    raise HTTPException(status_code=500, detail="CAD file was not generated")
                    
            finally:
                # Clean up temporary files in case of errors
                if script_path and os.path.exists(script_path):
                    try:
                        os.unlink(script_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to clean up temporary file: {cleanup_error}")
    
    except HTTPException:
        raise
        
    except Exception as e:
        generation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate model: {str(e)}"
        )

@app.get("/formats")
async def get_supported_formats():
    """Get list of supported output formats"""
    return {
        "supported_formats": [
            {"format": "stl", "description": "STL mesh format for 3D printing"},
            {"format": "step", "description": "STEP format for CAD exchange"},
            {"format": "obj", "description": "OBJ format for 3D graphics"},
            {"format": "dxf", "description": "DXF format for 2D drawings"},
            {"format": "dwg", "description": "DWG format for AutoCAD"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info",
        reload=True
    )
