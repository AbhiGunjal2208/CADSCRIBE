"""
AI service for natural language processing and code generation.
Integrated solution with Gemini 2.5 Flash, OpenRouter fallback, AWS S3 storage, and logging.
"""
import logging
import time
import re
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from google import genai
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI service for generating CAD code with Gemini primary and OpenRouter fallback."""
    
    def __init__(self):
        # API Keys
        self.gemini_api_key = settings.gemini_api_key
        self.openrouter_api_key = settings.openrouter_api_key
        
        # AWS S3 Configuration
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.aws_bucket_name = settings.aws_bucket_name
        self.aws_region = settings.aws_region
        
        # Initialize Gemini
        self._init_gemini()
        
        # Initialize OpenRouter
        self._init_openrouter()
        
        # Initialize S3 client
        self._init_s3_client()
        
        # Performance tracking
        self.performance_metrics = {
            "gemini_calls": 0,
            "gemini_successes": 0,
            "openrouter_calls": 0,
            "openrouter_successes": 0,
            "s3_uploads": 0,
            "s3_upload_failures": 0,
            "total_requests": 0
        }
    
    def clean_generated_code(self, code: str) -> str:
        """
        Clean AI-generated code by removing markdown formatting and extra whitespace.
        Based on the reference implementation from OpenRouter GUI.
        """
        if not code:
            return code
        
        # Remove markdown code blocks
        code = re.sub(r'```python\s*', '', code)
        code = re.sub(r'```\s*', '', code)
        
        # Remove any remaining backticks
        code = code.replace('`', '')
        
        # Remove extra whitespace at the beginning and end
        code = code.strip()
        
        # Remove any leading/trailing quotes that might wrap the code
        if code.startswith('"""') and code.endswith('"""'):
            code = code[3:-3].strip()
        elif code.startswith("'''") and code.endswith("'''"):
            code = code[3:-3].strip()
        
        # Remove any explanatory text that might be at the beginning
        lines = code.split('\n')
        cleaned_lines = []
        code_started = False
        
        for line in lines:
            stripped_line = line.strip()
            
            # Skip empty lines at the beginning
            if not code_started and not stripped_line:
                continue
                
            # Check if this looks like actual Python code
            if (stripped_line.startswith('import ') or 
                stripped_line.startswith('from ') or
                stripped_line.startswith('def ') or
                stripped_line.startswith('class ') or
                stripped_line.startswith('#') or
                '=' in stripped_line or
                stripped_line.startswith('if ') or
                stripped_line.startswith('for ') or
                stripped_line.startswith('while ') or
                stripped_line.startswith('try:') or
                stripped_line.startswith('with ') or
                code_started):
                code_started = True
                cleaned_lines.append(line)
            elif code_started:
                # Once code has started, include everything
                cleaned_lines.append(line)
        
        cleaned_code = '\n'.join(cleaned_lines).strip()
        
        # Fix CadQuery imports to prevent processing errors
        cleaned_code = self._fix_cadquery_imports(cleaned_code)
        
        logger.info(f"🧹 Code cleaned: {len(code)} → {len(cleaned_code)} characters")
        return cleaned_code
    
    def _fix_cadquery_imports(self, code: str) -> str:
        """Convert CadQuery code to FreeCAD format to prevent processing errors."""
        if not code:
            return code
        
        # Check if this is CadQuery code that needs conversion
        if 'import cadquery' in code or 'cq.Workplane' in code or 'show_object' in code:
            logger.warning("🔧 Detected CadQuery imports - converting to FreeCAD format")
            
            # Replace CadQuery imports with FreeCAD imports
            code = re.sub(r'import cadquery as cq\s*\n?', '', code)
            code = re.sub(r'import cadquery\s*\n?', '', code)
            code = re.sub(r'from cadquery import.*\n?', '', code)
            
            # Remove show_object calls
            code = re.sub(r'show_object\([^)]+\)\s*\n?', '', code)
            
            # Add FreeCAD imports at the beginning
            freecad_imports = """import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
"""
            
            # Simple conversion for basic shapes
            if 'cq.Workplane' in code and '.box(' in code:
                # Extract box dimensions if possible
                box_match = re.search(r'\.box\(([^)]+)\)', code)
                if box_match:
                    params = box_match.group(1).split(',')
                    if len(params) >= 3:
                        try:
                            w, h, d = [float(p.strip()) for p in params[:3]]
                            freecad_code = f"""cube = doc.addObject("Part::Box", "Cube")
cube.Length = {w}
cube.Width = {h}
cube.Height = {d}
doc.recompute()

# Multi-format export (HEADLESS)
output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{{base_name}}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{{base_name}}.stl")
    Mesh.export([cube], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{{base_name}}.obj")
    Mesh.export([cube], obj_path)
    
    # Export STEP
    step_path = os.path.join(output_dir, f"{{base_name}}.step")
    Part.export([cube], step_path)
    
    # Export IGES
    iges_path = os.path.join(output_dir, f"{{base_name}}.iges")
    Part.export([cube], iges_path)
    
except Exception as e:
    print(f"Export error: {{e}}")"""
                            
                            return freecad_imports + freecad_code
                        except ValueError:
                            pass
            
            elif 'cq.Workplane' in code and '.cylinder(' in code:
                # Convert cylinder
                cylinder_match = re.search(r'\.cylinder\(([^)]+)\)', code)
                if cylinder_match:
                    params = cylinder_match.group(1).split(',')
                    if len(params) >= 2:
                        try:
                            h, r = [float(p.strip()) for p in params[:2]]
                            freecad_code = f"""cylinder = doc.addObject("Part::Cylinder", "Cylinder")
cylinder.Radius = {r}
cylinder.Height = {h}
doc.recompute()

# Multi-format export (HEADLESS)
output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{{base_name}}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{{base_name}}.stl")
    Mesh.export([cylinder], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{{base_name}}.obj")
    Mesh.export([cylinder], obj_path)
    
    # Export STEP
    step_path = os.path.join(output_dir, f"{{base_name}}.step")
    Part.export([cylinder], step_path)
    
    # Export IGES
    iges_path = os.path.join(output_dir, f"{{base_name}}.iges")
    Part.export([cylinder], iges_path)
    
except Exception as e:
    print(f"Export error: {{e}}")"""
                            
                            return freecad_imports + freecad_code
                        except ValueError:
                            pass
            
            # Fallback: create a default cube with FreeCAD format
            logger.warning("🔧 Using fallback FreeCAD cube for CadQuery conversion")
            fallback_code = """cube = doc.addObject("Part::Box", "Cube")
cube.Length = 10
cube.Width = 10
cube.Height = 10
doc.recompute()

# Multi-format export (HEADLESS)
output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{base_name}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{base_name}.stl")
    Mesh.export([cube], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{base_name}.obj")
    Mesh.export([cube], obj_path)
    
    # Export STEP
    step_path = os.path.join(output_dir, f"{base_name}.step")
    Part.export([cube], step_path)
    
    # Export IGES
    iges_path = os.path.join(output_dir, f"{base_name}.iges")
    Part.export([cube], iges_path)
    
except Exception as e:
    print(f"Export error: {e}")"""
            
            return freecad_imports + fallback_code
        
        return code
    
    def _enforce_headless_mode(self, code: str) -> str:
        """Aggressively enforce headless mode by removing/replacing GUI imports and calls."""
        if not code:
            return code
            
        logger.info("🔒 Enforcing headless mode - removing GUI components")
        
        # Split into lines for processing
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            line_lower = line.lower().strip()
            original_line = line
            
            # Remove or replace GUI imports
            if any(gui_import in line_lower for gui_import in [
                'import freecadgui', 'from freecadgui', 'import importgui', 
                'from importgui', 'freecadgui.', 'importgui.'
            ]):
                logger.warning(f"🚫 Removing GUI import: {line.strip()}")
                # Skip this line entirely
                continue
            
            # Replace GUI export calls with headless alternatives
            if 'importgui.export' in line_lower:
                logger.warning(f"🔄 Converting GUI export to headless: {line.strip()}")
                # Replace ImportGui.export with Part.export for STEP/IGES
                if '.step' in line_lower or '.iges' in line_lower:
                    line = line.replace('ImportGui.export', 'Part.export')
                else:
                    # For other formats, skip or convert to Mesh.export
                    line = line.replace('ImportGui.export', 'Mesh.export')
            
            # Replace any remaining GUI references
            if 'freecadgui' in line_lower:
                logger.warning(f"🚫 Removing FreeCADGui reference: {line.strip()}")
                continue
                
            processed_lines.append(line)
        
        # Reconstruct the code
        processed_code = '\n'.join(processed_lines)
        
        # Ensure proper headless imports are present
        if 'import FreeCAD' not in processed_code:
            processed_code = 'import FreeCAD, Part, Mesh\nimport os\n\n' + processed_code
        
        # Log if any changes were made
        if len(processed_lines) != len(lines):
            logger.info(f"✅ Headless enforcement: {len(lines)} → {len(processed_lines)} lines (removed {len(lines) - len(processed_lines)} GUI lines)")
        
        return processed_code
    
    def _contains_gui_imports(self, code: str) -> bool:
        """Check if code still contains any GUI imports or references."""
        if not code:
            return False
            
        code_lower = code.lower()
        gui_patterns = [
            'import freecadgui',
            'from freecadgui',
            'import importgui',
            'from importgui',
            'freecadgui.',
            'importgui.'
        ]
        
        for pattern in gui_patterns:
            if pattern in code_lower:
                logger.warning(f"🚫 GUI pattern detected: {pattern}")
                return True
                
        return False
    
    async def generate_code_fix(self, fix_prompt: str) -> str:
        """Generate a fixed script using AI based on error analysis."""
        try:
            logger.info("🤖 Using AI to generate intelligent script fix")
            logger.debug(f"Fix prompt (first 200 chars): {fix_prompt[:200]}...")
            
            # Try Gemini first
            if self.gemini_client:
                try:
                    logger.info("🔄 Attempting Gemini fix...")
                    response = await asyncio.to_thread(
                        self.gemini_client.models.generate_content,
                        model="gemini-2.0-flash-exp",
                        contents=fix_prompt
                    )
                    
                    if response.text:
                        logger.info(f"📝 Gemini response length: {len(response.text)} chars")
                        fixed_code = self.clean_generated_code(response.text)
                        logger.info(f"🧹 Cleaned code length: {len(fixed_code) if fixed_code else 0} chars")
                        
                        if fixed_code and 'import FreeCAD' in fixed_code:
                            logger.info("✅ Gemini generated successful FreeCAD fix")
                            return fixed_code
                        else:
                            logger.warning("⚠️ Gemini response doesn't contain valid FreeCAD code")
                except Exception as e:
                    logger.warning(f"Gemini fix failed: {e}")
            
            # Try OpenRouter as fallback
            if self.openrouter_client:
                try:
                    logger.info("🔄 Attempting OpenRouter fix...")
                    response = await self.openrouter_client.chat.completions.create(
                        model="anthropic/claude-3.5-sonnet",
                        messages=[{"role": "user", "content": fix_prompt}],
                        max_tokens=2000,
                        temperature=0.1  # Low temperature for more deterministic fixes
                    )
                    
                    if response.choices and response.choices[0].message.content:
                        content = response.choices[0].message.content
                        logger.info(f"📝 OpenRouter response length: {len(content)} chars")
                        fixed_code = self.clean_generated_code(content)
                        logger.info(f"🧹 Cleaned code length: {len(fixed_code) if fixed_code else 0} chars")
                        
                        if fixed_code and 'import FreeCAD' in fixed_code:
                            logger.info("✅ OpenRouter generated successful FreeCAD fix")
                            return fixed_code
                        else:
                            logger.warning("⚠️ OpenRouter response doesn't contain valid FreeCAD code")
                except Exception as e:
                    logger.warning(f"OpenRouter fix failed: {e}")
            
            logger.warning("🤖 AI fix generation failed - no valid response from any provider")
            return None
            
        except Exception as e:
            logger.error(f"❌ AI fix generation error: {e}")
            return None
    
    def _init_gemini(self):
        """Initialize Gemini AI with official SDK."""
        if self.gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                logger.info("✅ Gemini 2.5 Flash initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.gemini_client = None
        else:
            logger.warning("⚠️ Gemini API key not configured")
            self.gemini_client = None
    
    def _init_openrouter(self):
        """Initialize OpenRouter client."""
        if self.openrouter_api_key:
            try:
                self.openrouter_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.openrouter_api_key
                )
                logger.info("✅ OpenRouter initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenRouter: {e}")
                self.openrouter_client = None
        else:
            logger.warning("⚠️ OpenRouter API key not configured")
            self.openrouter_client = None
    
    def _init_s3_client(self):
        """Initialize AWS S3 client."""
        if all([self.aws_access_key_id, self.aws_secret_access_key, self.aws_bucket_name]):
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.aws_region
                )
                logger.info("✅ AWS S3 client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize S3 client: {e}")
                self.s3_client = None
        else:
            logger.warning("⚠️ AWS S3 credentials not fully configured")
            self.s3_client = None
    
    async def generate_cad_code(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate Python CAD code from natural language input.
        Primary: Gemini 2.5 Flash, Fallback: OpenRouter
        """
        start_time = time.time()
        generated_code = None
        source_model = None
        confidence = None
        
        try:
            # Step 1: Try Gemini 2.5 Flash first
            logger.info(f"🚀 Starting CAD code generation for: '{user_input[:50]}...'")
            
            if self.gemini_client:
                logger.info("🔄 Attempting Gemini 2.5 Flash...")
                generated_code, confidence = await self._call_gemini_api(user_input, context)
                if generated_code:
                    source_model = "Gemini"
                    self.performance_metrics["gemini_successes"] += 1
                    logger.info("✅ Gemini 2.5 Flash succeeded")
                else:
                    logger.warning("⚠️ Gemini 2.5 Flash failed, switching to OpenRouter...")
            
            # Step 2: Fallback to OpenRouter if Gemini failed
            if not generated_code and self.openrouter_client:
                logger.info("🔄 Switching to OpenRouter fallback...")
                generated_code, confidence = await self._call_openrouter_api(user_input, context)
                if generated_code:
                    source_model = "OpenRouter"
                    self.performance_metrics["openrouter_successes"] += 1
                    logger.info("✅ OpenRouter fallback succeeded")
                else:
                    logger.error("❌ OpenRouter fallback also failed")
            
            # Step 3: Final fallback to mock if both AI services failed
            if not generated_code:
                logger.warning("🔄 Both AI services failed, using mock generation...")
                generated_code = await self._generate_mock_code(user_input)
                source_model = "Mock"
                confidence = 0.5
            
            # Step 3.5: Clean the generated code to remove markdown formatting
            if generated_code:
                original_length = len(generated_code)
                generated_code = self._fix_cadquery_imports(generated_code)
                generated_code = self._enforce_headless_mode(generated_code)
                generated_code = self.clean_generated_code(generated_code)
                
                # Final validation - reject if still contains GUI imports
                if self._contains_gui_imports(generated_code):
                    logger.error("🚫 Generated code still contains GUI imports after processing - using fallback")
                    generated_code = await self._generate_mock_code(user_input)
                    source_model = "Fallback (GUI detected)"
                    confidence = 0.3
                
                logger.info(f"🧹 Code cleaned: {original_length} → {len(generated_code)} characters")
            
            # Step 4: Upload to S3 and update project if code was generated
            s3_result = None
            if generated_code and context and context.get('project_id'):
                user_id = context.get('user_id')
                project_id = context['project_id']
                s3_result = await self._upload_to_s3(generated_code, project_id, user_id)
                
                # Update project with new version and AI model info
                if s3_result and s3_result.get('success'):
                    await self._update_project_after_generation(
                        project_id, s3_result, source_model, user_id
                    )
            
            # Step 5: Calculate response time
            response_time = time.time() - start_time
            current_timestamp = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✅ Code generation completed in {response_time:.2f}s using {source_model}")
            
            return {
                "generated_code": generated_code,
                "timestamp": current_timestamp,
                "confidence": confidence,
                "source_model": source_model,
                "response_time": response_time,
                "s3_result": s3_result,
                "s3_url": s3_result["s3_path"] if s3_result else None,
                "script_version": s3_result["version"] if s3_result else None,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Critical error in generate_cad_code: {e}")
            return {
                "generated_code": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "confidence": None,
                "source_model": None,
                "error": str(e),
                "success": False
            }
    
    async def _call_gemini_api(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> tuple[Optional[str], Optional[float]]:
        """Call Gemini 2.5 Flash API using official SDK."""
        if not self.gemini_client:
            return None, None
        
        self.performance_metrics["gemini_calls"] += 1
        
        try:
            # Create comprehensive prompt for CAD code generation
            prompt = self._create_cad_prompt(user_input, context)
            
            # Make API call with retries
            for attempt in range(3):
                try:
                    start_time = time.time()
                    response = await asyncio.to_thread(
                        self.gemini_client.models.generate_content,
                        model="gemini-2.0-flash-exp",
                        contents=prompt
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.text:
                        # Extract Python code from response
                        python_code = self._extract_python_code(response.text)
                        if python_code:
                            # Calculate confidence based on response quality
                            confidence = self._calculate_confidence(python_code, user_input)
                            logger.info(f"✅ Gemini success! Response time: {response_time:.2f} seconds")
                            return python_code, confidence
                    
                    logger.warning(f"Gemini attempt {attempt + 1}: No valid code generated")
                    
                except Exception as e:
                    logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
                    if attempt < 2:  # Don't sleep on last attempt
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
            
            logger.error("All Gemini attempts failed")
            return None, None
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None, None
    
    async def _call_openrouter_api(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> tuple[Optional[str], Optional[float]]:
        """Call OpenRouter API as fallback."""
        if not self.openrouter_client:
            return None, None
        
        self.performance_metrics["openrouter_calls"] += 1
        
        try:
            prompt = self._create_cad_prompt(user_input, context)
            
            # Make API call with retries and exponential backoff
            for attempt in range(3):
                try:
                    start_time = time.time()
                    
                    completion = await asyncio.to_thread(
                        self.openrouter_client.chat.completions.create,
                        extra_headers={
                            "HTTP-Referer": "https://cadscribe.ai",
                            "X-Title": "CADSCRIBE",
                        },
                        model="openai/gpt-oss-20b:free",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=1500,
                        temperature=0.1
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if completion.choices and completion.choices[0].message.content:
                        content = completion.choices[0].message.content
                        python_code = self._extract_python_code(content)
                        if python_code:
                            confidence = self._calculate_confidence(python_code, user_input)
                            logger.info(f"✅ OpenRouter success! Response time: {response_time:.2f} seconds")
                            return python_code, confidence
                    
                    logger.warning(f"OpenRouter attempt {attempt + 1}: No valid code generated")
                        
                except Exception as e:
                    logger.error(f"OpenRouter attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                    continue
            
            logger.error("All OpenRouter attempts failed")
            return None, None
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return None, None
    
    async def _upload_to_s3(self, code: str, project_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Upload generated Python script to S3 with versioning."""
        try:
            # Import S3 service here to avoid circular imports
            from services.s3_service import s3_service
            
            # Use the new S3 service with versioning
            upload_result = await s3_service.upload_script(
                code=code,
                project_name=project_id,
                user_id=user_id
            )
            
            if upload_result["success"]:
                self.performance_metrics["s3_uploads"] += 1
                logger.info(f"✅ Code uploaded to S3 with versioning: {upload_result['s3_path']}")
                return upload_result
            else:
                self.performance_metrics["s3_upload_failures"] += 1
                logger.error(f"❌ S3 upload failed: {upload_result.get('error', 'Unknown error')}")
                return None
            
        except Exception as e:
            self.performance_metrics["s3_upload_failures"] += 1
            logger.error(f"❌ S3 upload error: {e}")
            return None
    
    async def _update_project_after_generation(self, project_id: str, s3_result: Dict[str, Any], 
                                             ai_model: str, user_id: str) -> None:
        """Update project and create file record after successful code generation."""
        try:
            # Import here to avoid circular imports
            from services.project_service import project_service
            from models.schema import FileType
            
            version = s3_result.get('version', 1)
            s3_path = s3_result.get('s3_path')
            
            # Update project with new version and status
            project_service.update_project_version(
                project_id=project_id,
                version=version,
                ai_model=ai_model,
                s3_input_path=s3_path
            )
            
            # Create file record
            file_data = {
                "project_id": project_id,
                "version": version,
                "file_type": FileType.INPUT.value,
                "s3_path": s3_path,
                "timestamp": datetime.now(timezone.utc),
                "metadata": {
                    "file_name": s3_path.split("/")[-1] if "/" in s3_path else s3_path,
                    "ai_model": ai_model,
                    "uploaded_by": user_id,
                    "generated_by": "cadscribe-ai",
                    "confidence": s3_result.get('metadata', {}).get('confidence'),
                    "generation_source": "ai_service"
                }
            }
            
            project_service.create_file_record(file_data)
            logger.info(f"✅ Updated project {project_id} with version {version}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update project after generation: {e}")
    
    def _create_cad_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Create comprehensive prompt for CAD code generation with multi-format export."""
        base_prompt = f"""Generate only the Python script code for FreeCAD HEADLESS to create {user_input}. Return only the executable Python code without any explanations, markdown formatting, comments, or instructions. Just the raw Python script that can be directly executed.

CRITICAL REQUIREMENTS - HEADLESS EXECUTION ONLY:
- Use FreeCAD library in HEADLESS mode (import FreeCAD, Part, Mesh, os)
- ABSOLUTELY FORBIDDEN: ImportGui, FreeCADGui, or ANY GUI components
- FORBIDDEN IMPORTS: import FreeCADGui, import ImportGui, from FreeCADGui, from ImportGui
- NO GUI DEPENDENCIES - this script runs on a server without display
- Create 3D models using FreeCAD Part workbench only
- MUST include automatic export to ALL 5 formats: .fcstd, .stl, .obj, .step, .iges
- Use the exact export template provided below
- Return ONLY Python code, no explanations or markdown
- HEADLESS MODE ONLY - no visual interface required
- COMMAND LINE EXECUTION ONLY - no GUI allowed

FORBIDDEN CODE PATTERNS (DO NOT USE):
- import FreeCADGui
- import ImportGui  
- FreeCADGui.anything
- ImportGui.anything
- Any GUI-related functions

"""
        
        if context and context.get('parameters'):
            base_prompt += f"Parameters: {context['parameters']}\n"
        
        # Extra emphasis on headless mode if explicitly requested
        if context and context.get('headless'):
            base_prompt += """
EXTRA EMPHASIS - HEADLESS MODE REQUIRED:
- This script will run on a SERVER without any display or GUI
- ABSOLUTELY NO ImportGui, FreeCADGui, or visual components
- Must work in pure command-line environment
- No user interaction or display required

"""
        
        base_prompt += """
REQUIRED TEMPLATE - MUST use this exact export structure:
import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")

# Create your 3D model here (replace this example)
cube = doc.addObject("Part::Box", "Cube")
cube.Length = 10
cube.Width = 10
cube.Height = 10
doc.recompute()

# REQUIRED: Multi-format export (DO NOT MODIFY)
output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

# Export to different formats (HEADLESS - no ImportGui)
try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{base_name}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{base_name}.stl")
    Mesh.export([cube], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{base_name}.obj")
    Mesh.export([cube], obj_path)
    
    # Export STEP (using Part module directly)
    step_path = os.path.join(output_dir, f"{base_name}.step")
    Part.export([cube], step_path)
    
    # Export IGES (alternative to GLTF for CAD)
    iges_path = os.path.join(output_dir, f"{base_name}.iges")
    Part.export([cube], iges_path)
    
except Exception as e:
    print(f"Export error: {e}")

IMPORTANT: Replace 'cube' in the export functions with your actual object variable name.
"""
        return base_prompt
    
    def _extract_python_code(self, text: str) -> Optional[str]:
        """Extract Python code from AI response."""
        if not text:
            return None
        
        # Remove markdown code blocks
        code_block_pattern = r'```(?:python)?\s*(.*?)\s*```'
        matches = re.findall(code_block_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            code = matches[0].strip()
        else:
            # If no code blocks, try to extract lines that look like Python
            lines = text.split('\n')
            python_lines = []
            for line in lines:
                stripped = line.strip()
                if (stripped.startswith('import ') or 
                    stripped.startswith('from ') or
                    stripped.startswith('doc = ') or
                    stripped.startswith('cube = ') or
                    'FreeCAD' in stripped or
                    'addObject(' in stripped or
                    'doc.recompute()' in stripped or
                    'formats = {' in stripped or
                    '.box(' in stripped or
                    '.cylinder(' in stripped):
                    python_lines.append(line)
            code = '\n'.join(python_lines) if python_lines else text.strip()
        
        # Validate that it's actually Python code (FreeCAD or CadQuery)
        if ('import FreeCAD' in code or 
            'import cadquery' in code or 
            'cq.Workplane' in code or
            'doc.addObject' in code):
            return code
        
        return None
    
    def _calculate_confidence(self, code: str, user_input: str) -> float:
        """Calculate confidence score based on code quality and relevance."""
        confidence = 0.5  # Base confidence
        
        # Check for FreeCAD imports (preferred)
        if 'import FreeCAD' in code:
            confidence += 0.3
        elif 'import cadquery' in code or 'import cq' in code:
            confidence += 0.2
        
        # Check for FreeCAD document creation
        if 'FreeCAD.newDocument' in code:
            confidence += 0.1
        
        # Check for multi-format export
        if 'formats = {' in code and '.fcstd' in code and '.stl' in code:
            confidence += 0.2
        
        # Check for workplane usage (CadQuery)
        if 'cq.Workplane' in code:
            confidence += 0.1
        
        # Check for FreeCAD object creation
        if 'addObject(' in code:
            confidence += 0.1
        
        # Check for relevant keywords from user input
        user_words = user_input.lower().split()
        code_lower = code.lower()
        
        relevant_keywords = ['box', 'cylinder', 'sphere', 'cone', 'extrude', 'revolve']
        for word in user_words:
            if word in relevant_keywords and word in code_lower:
                confidence += 0.05
        
        return min(confidence, 1.0)
    
    async def _generate_mock_code(self, user_input: str) -> str:
        """Generate mock FreeCAD code for testing with multi-format export."""
        user_input_lower = user_input.lower()
        
        # Parse dimensions from input
        dimensions = re.findall(r'\d+\.?\d*', user_input)
        x, y, z = (float(dimensions[i]) if i < len(dimensions) else 10.0 for i in range(3))
        
        if "cube" in user_input_lower or "box" in user_input_lower:
            return f'''import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
cube = doc.addObject("Part::Box", "Cube")
cube.Length = {x}
cube.Width = {y}
cube.Height = {z}
doc.recompute()

output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{{base_name}}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{{base_name}}.stl")
    Mesh.export([cube], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{{base_name}}.obj")
    Mesh.export([cube], obj_path)
    
    # Export STEP
    step_path = os.path.join(output_dir, f"{{base_name}}.step")
    Part.export([cube], step_path)
    
    # Export IGES
    iges_path = os.path.join(output_dir, f"{{base_name}}.iges")
    Part.export([cube], iges_path)
    
except Exception as e:
    print(f"Export error: {{e}}")'''
        
        elif "cylinder" in user_input_lower or "tube" in user_input_lower:
            return f'''import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
cylinder = doc.addObject("Part::Cylinder", "Cylinder")
cylinder.Radius = {x/2}
cylinder.Height = {z}
doc.recompute()

output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{{base_name}}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{{base_name}}.stl")
    Mesh.export([cylinder], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{{base_name}}.obj")
    Mesh.export([cylinder], obj_path)
    
    # Export STEP
    step_path = os.path.join(output_dir, f"{{base_name}}.step")
    Part.export([cylinder], step_path)
    
    # Export IGES
    iges_path = os.path.join(output_dir, f"{{base_name}}.iges")
    Part.export([cylinder], iges_path)
    
except Exception as e:
    print(f"Export error: {{e}}")'''
        
        elif "sphere" in user_input_lower or "ball" in user_input_lower:
            return f'''import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
sphere = doc.addObject("Part::Sphere", "Sphere")
sphere.Radius = {x/2}
doc.recompute()

output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{{base_name}}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{{base_name}}.stl")
    Mesh.export([sphere], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{{base_name}}.obj")
    Mesh.export([sphere], obj_path)
    
    # Export STEP
    step_path = os.path.join(output_dir, f"{{base_name}}.step")
    Part.export([sphere], step_path)
    
    # Export IGES
    iges_path = os.path.join(output_dir, f"{{base_name}}.iges")
    Part.export([sphere], iges_path)
    
except Exception as e:
    print(f"Export error: {{e}}")'''
        
        else:
            # Default generic shape (cube)
            return f'''import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
cube = doc.addObject("Part::Box", "Cube")
cube.Length = {x}
cube.Width = {y}
cube.Height = {z}
doc.recompute()

output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{{base_name}}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{{base_name}}.stl")
    Mesh.export([cube], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{{base_name}}.obj")
    Mesh.export([cube], obj_path)
    
    # Export STEP
    step_path = os.path.join(output_dir, f"{{base_name}}.step")
    Part.export([cube], step_path)
    
    # Export IGES
    iges_path = os.path.join(output_dir, f"{{base_name}}.iges")
    Part.export([cube], iges_path)
    
except Exception as e:
    print(f"Export error: {{e}}")'''
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        total_calls = self.performance_metrics["gemini_calls"] + self.performance_metrics["openrouter_calls"]
        total_successes = self.performance_metrics["gemini_successes"] + self.performance_metrics["openrouter_successes"]
        
        return {
            "total_requests": total_calls,
            "total_successes": total_successes,
            "success_rate": (total_successes / total_calls * 100) if total_calls > 0 else 0,
            "gemini_success_rate": (self.performance_metrics["gemini_successes"] / self.performance_metrics["gemini_calls"] * 100) if self.performance_metrics["gemini_calls"] > 0 else 0,
            "openrouter_success_rate": (self.performance_metrics["openrouter_successes"] / self.performance_metrics["openrouter_calls"] * 100) if self.performance_metrics["openrouter_calls"] > 0 else 0,
            "s3_upload_success_rate": (self.performance_metrics["s3_uploads"] / (self.performance_metrics["s3_uploads"] + self.performance_metrics["s3_upload_failures"]) * 100) if (self.performance_metrics["s3_uploads"] + self.performance_metrics["s3_upload_failures"]) > 0 else 0,
            "detailed_metrics": self.performance_metrics
        }


# Global AI service instance
ai_service = AIService()
