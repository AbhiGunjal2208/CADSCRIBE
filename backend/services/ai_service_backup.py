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
            "s3_upload_failures": 0
        }
    
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
        
        Args:
            user_input: Natural language description of the CAD model
            context: Additional context (project_id, previous messages, parameters, etc.)
        
        Returns:
            Dict containing generated code, timestamp, confidence, and source model
        """
        start_time = time.time()
        generated_code = None
        source_model = None
        confidence = None
        
        try:
            # Step 1: Try Gemini 2.5 Flash first
            logger.info(f"🚀 Starting CAD code generation for: '{user_input[:50]}...'")
            
            if self.gemini_model:
                logger.info("🔄 Attempting Gemini 2.5 Flash...")
                generated_code, confidence = await self._call_gemini_api(user_input, context)
                if generated_code:
                    source_model = "Gemini"
                    self.performance_metrics["gemini_successes"] += 1
                    logger.info("✅ Gemini 2.5 Flash succeeded")
                else:
                    logger.warning("⚠️ Gemini 2.5 Flash failed, switching to OpenRouter...")
            
            # Step 2: Fallback to OpenRouter if Gemini failed
            if not generated_code and self.openrouter_api_key:
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
            
            # Step 4: Upload to S3 if code was generated
            s3_url = None
            if generated_code and context and context.get('project_id'):
                s3_url = await self._upload_to_s3(generated_code, context['project_id'])
            
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
                "s3_url": s3_url,
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
        if not self.gemini_model:
            return None, None
        
        self.performance_metrics["gemini_calls"] += 1
        
        try:
            # Create comprehensive prompt for CAD code generation
            prompt = self._create_cad_prompt(user_input, context)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048,
                top_p=0.8,
                top_k=40
            )
            
            # Make API call with retries
            for attempt in range(3):
                try:
                    response = await asyncio.to_thread(
                        self.gemini_model.generate_content,
                        prompt,
                        generation_config=generation_config
                    )
                    
                    if response.text:
                        # Extract Python code from response
                        python_code = self._extract_python_code(response.text)
                        if python_code:
                            # Calculate confidence based on response quality
                            confidence = self._calculate_confidence(python_code, user_input)
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
        if not self.openrouter_api_key:
            return None, None
        
        self.performance_metrics["openrouter_calls"] += 1
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://cadscribe.ai",
                "X-Title": "CADSCRIBE"
            }
            
            prompt = self._create_cad_prompt(user_input, context)
            
            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a CAD expert. Generate ONLY Python CadQuery code. Return pure Python code without markdown, explanations, or comments outside the code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.1,
                "top_p": 0.9
            }
            
            # Make API call with retries and exponential backoff
            for attempt in range(3):
                try:
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "choices" in result and result["choices"]:
                            content = result["choices"][0]["message"]["content"]
                            python_code = self._extract_python_code(content)
                            if python_code:
                                confidence = self._calculate_confidence(python_code, user_input)
                                return python_code, confidence
                    
                    elif response.status_code == 429:  # Rate limit
                        wait_time = 2 ** attempt
                        logger.warning(f"OpenRouter rate limited, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"OpenRouter timeout on attempt {attempt + 1}")
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                    continue
                
                except Exception as e:
                    logger.error(f"OpenRouter request error: {e}")
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                    continue
            
            logger.error("All OpenRouter attempts failed")
            return None, None
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return None, None
    
    async def _upload_to_s3(self, code: str, project_id: str) -> Optional[str]:
        """Upload generated Python script to S3."""
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured, skipping upload")
            return None
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"input/{project_id}_{timestamp}.py"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=filename,
                Body=code.encode('utf-8'),
                ContentType='text/x-python',
                Metadata={
                    'project_id': project_id,
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'service': 'cadscribe-ai'
                }
            )
            
            s3_url = f"s3://{self.aws_bucket_name}/{filename}"
            self.performance_metrics["s3_uploads"] += 1
            logger.info(f"✅ Code uploaded to S3: {s3_url}")
            return s3_url
            
        except ClientError as e:
            self.performance_metrics["s3_upload_failures"] += 1
            logger.error(f"❌ S3 upload failed: {e}")
            return None
        except Exception as e:
            self.performance_metrics["s3_upload_failures"] += 1
            logger.error(f"❌ S3 upload error: {e}")
            return None
    
    def _create_cad_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Create comprehensive prompt for CAD code generation."""
        base_prompt = f"""Generate Python CadQuery code for: {user_input}

Requirements:
- Use CadQuery library (import cadquery as cq)
- Create parametric 3D models
- Include proper workplane operations
- Add show_object(result) at the end
- Return ONLY Python code, no explanations or markdown

"""
        
        if context and context.get('parameters'):
            base_prompt += f"Parameters: {context['parameters']}\n"
        
        base_prompt += """
Example format:
import cadquery as cq

result = (
    cq.Workplane("XY")
    .box(10, 10, 10)
)

show_object(result)
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
                    stripped.startswith('result = ') or
                    stripped.startswith('show_object(') or
                    'cq.Workplane' in stripped or
                    '.box(' in stripped or
                    '.cylinder(' in stripped):
                    python_lines.append(line)
            code = '\n'.join(python_lines) if python_lines else text.strip()
        
        # Validate that it's actually Python code
        if 'import cadquery' in code or 'cq.Workplane' in code:
            return code
        
        return None
    
    def _calculate_confidence(self, code: str, user_input: str) -> float:
        """Calculate confidence score based on code quality and relevance."""
        confidence = 0.5  # Base confidence
        
        # Check for CadQuery imports
        if 'import cadquery' in code or 'import cq' in code:
            confidence += 0.2
        
        # Check for workplane usage
        if 'cq.Workplane' in code:
            confidence += 0.1
        
        # Check for show_object
        if 'show_object' in code:
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
        """Generate mock CAD code for testing."""
        user_input_lower = user_input.lower()
        
        # Parse dimensions from input
        dimensions = re.findall(r'\d+\.?\d*', user_input)
        x, y, z = (float(dimensions[i]) if i < len(dimensions) else 10.0 for i in range(3))
        
        if "cube" in user_input_lower or "box" in user_input_lower:
            return f'''import cadquery as cq

result = (
    cq.Workplane("XY")
    .box({x}, {y}, {z})
)

show_object(result)'''
        
        elif "cylinder" in user_input_lower or "tube" in user_input_lower:
            return f'''import cadquery as cq

result = (
    cq.Workplane("XY")
    .circle({x/2})
    .extrude({z})
)

show_object(result)'''
        
        elif "sphere" in user_input_lower or "ball" in user_input_lower:
            return f'''import cadquery as cq

result = (
    cq.Workplane("XY")
    .sphere({x/2})
)

show_object(result)'''
        
        else:
            # Default generic shape
            return f'''import cadquery as cq

result = (
    cq.Workplane("XY")
    .box({x}, {y}, {z})
)

show_object(result)'''
    
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
