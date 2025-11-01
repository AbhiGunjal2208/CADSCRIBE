"""
S3 service for managing CAD scripts and outputs with automatic versioning.
Handles the complete AI-to-S3 script flow with output retrieval.
"""
import logging
import re
import asyncio
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config.settings import settings

logger = logging.getLogger(__name__)


class S3Service:
    """S3 service for managing CAD scripts with automatic versioning."""
    
    def __init__(self):
        """Initialize S3 service with AWS configuration."""
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.aws_bucket_name = settings.aws_bucket_name
        self.aws_region = settings.aws_region
        
        # Initialize S3 client
        self._init_s3_client()
        
        # Performance tracking
        self.performance_metrics = {
            "uploads": 0,
            "upload_failures": 0,
            "downloads": 0,
            "download_failures": 0,
            "version_checks": 0
        }
    
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
    
    async def get_next_version(self, project_name: str) -> int:
        """
        Get the next version number for a project by checking existing files.
        Returns 1 if no files exist, otherwise returns highest version + 1.
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured, returning version 1")
            return 1
        
        try:
            self.performance_metrics["version_checks"] += 1
            
            # List objects in the input directory for this project
            prefix = f"input/{project_name}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.aws_bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.info(f"No existing files for project {project_name}, starting with version 1")
                return 1
            
            # Extract version numbers from existing files
            version_pattern = re.compile(rf"{re.escape(project_name)}_v(\d+)\.py$")
            versions = []
            
            for obj in response['Contents']:
                key = obj['Key']
                match = version_pattern.search(key)
                if match:
                    versions.append(int(match.group(1)))
            
            if not versions:
                logger.info(f"No versioned files found for project {project_name}, starting with version 1")
                return 1
            
            next_version = max(versions) + 1
            logger.info(f"Next version for project {project_name}: v{next_version}")
            return next_version
            
        except ClientError as e:
            logger.error(f"❌ S3 error getting next version: {e}")
            return 1
        except Exception as e:
            logger.error(f"❌ Error getting next version: {e}")
            return 1
    
    async def upload_script(self, code: str, project_name: str, user_id: str = None) -> Dict[str, Any]:
        """
        Upload Python script to S3 with automatic versioning.
        
        Args:
            code: Python script content
            project_name: Name of the project
            user_id: Optional user ID for metadata
            
        Returns:
            Dict containing upload result with S3 path, version, and metadata
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured, skipping upload")
            return {
                "success": False,
                "error": "S3 not configured",
                "s3_path": None,
                "version": None
            }
        
        try:
            # Get next version number
            version = await self.get_next_version(project_name)
            
            # Generate filename with version
            filename = f"input/{project_name}/{project_name}_v{version}.py"
            
            # Prepare metadata
            current_time = datetime.now(timezone.utc).isoformat()
            metadata = {
                "project_id": project_name,
                "version": str(version),
                "generated_at": current_time,
                "service": "cadscribe-ai"
            }
            
            if user_id:
                metadata["user_id"] = user_id
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=filename,
                Body=code.encode('utf-8'),
                ContentType='text/x-python',
                ContentEncoding='utf-8',
                Metadata=metadata
            )
            
            s3_path = f"s3://{self.aws_bucket_name}/{filename}"
            self.performance_metrics["uploads"] += 1
            
            logger.info(f"✅ Script uploaded to S3: {s3_path}")
            
            return {
                "success": True,
                "s3_path": s3_path,
                "filename": filename,
                "version": version,
                "metadata": metadata,
                "upload_time": current_time
            }
            
        except ClientError as e:
            self.performance_metrics["upload_failures"] += 1
            logger.error(f"❌ S3 upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "s3_path": None,
                "version": None
            }
        except Exception as e:
            self.performance_metrics["upload_failures"] += 1
            logger.error(f"❌ Script upload error: {e}")
            return {
                "success": False,
                "error": str(e),
                "s3_path": None,
                "version": None
            }
    
    async def list_project_scripts(self, project_name: str) -> List[Dict[str, Any]]:
        """
        List all script versions for a project.
        
        Returns:
            List of script information including version, upload time, and metadata
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return []
        
        try:
            prefix = f"input/{project_name}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.aws_bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            scripts = []
            version_pattern = re.compile(rf"{re.escape(project_name)}_v(\d+)\.py$")
            
            for obj in response['Contents']:
                key = obj['Key']
                match = version_pattern.search(key)
                if match:
                    version = int(match.group(1))
                    
                    # Get object metadata
                    try:
                        head_response = self.s3_client.head_object(
                            Bucket=self.aws_bucket_name,
                            Key=key
                        )
                        metadata = head_response.get('Metadata', {})
                    except:
                        metadata = {}
                    
                    scripts.append({
                        "version": version,
                        "key": key,
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat(),
                        "metadata": metadata
                    })
            
            # Sort by version number (descending)
            scripts.sort(key=lambda x: x['version'], reverse=True)
            return scripts
            
        except ClientError as e:
            logger.error(f"❌ S3 error listing scripts: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error listing scripts: {e}")
            return []
    
    async def get_script_content(self, project_name: str, version: int) -> Optional[str]:
        """
        Get the content of a specific script version.
        
        Args:
            project_name: Name of the project
            version: Version number to retrieve
            
        Returns:
            Script content as string, or None if not found
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return None
        
        try:
            key = f"input/{project_name}/{project_name}_v{version}.py"
            
            response = self.s3_client.get_object(
                Bucket=self.aws_bucket_name,
                Key=key
            )
            
            content = response['Body'].read().decode('utf-8')
            self.performance_metrics["downloads"] += 1
            
            logger.info(f"✅ Retrieved script content: {key}")
            return content
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Script not found: {project_name}_v{version}.py")
            else:
                logger.error(f"❌ S3 error getting script: {e}")
            self.performance_metrics["download_failures"] += 1
            return None
        except Exception as e:
            logger.error(f"❌ Error getting script content: {e}")
            self.performance_metrics["download_failures"] += 1
            return None
    
    async def check_output_files(self, project_name: str, version: int = None) -> List[Dict[str, Any]]:
        """
        Check for output files (FCStd, STL, STEP, OBJ) for a project.
        Now supports versioned output folders.
        
        Args:
            project_name: Name of the project
            version: Specific version to check, or None for latest
        
        Returns:
            List of available output files with metadata including version info
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return []
        
        try:
            if version:
                # Check specific version folder
                prefix = f"output/{project_name}/v{version}/"
            else:
                # Check all version folders for latest
                prefix = f"output/{project_name}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.aws_bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            output_files = []
            supported_extensions = ['.FCStd', '.STL', '.STEP', '.IGES', '.OBJ', '.GLTF']
            version_pattern = re.compile(r'/v(\d+)/')
            
            for obj in response['Contents']:
                key = obj['Key']
                filename = key.split('/')[-1]
                
                # Skip metadata.json files
                if filename == 'metadata.json':
                    continue
                
                # Extract version from path
                version_match = version_pattern.search(key)
                file_version = int(version_match.group(1)) if version_match else None
                
                # Check if it's a supported output format
                if any(filename.upper().endswith(ext.upper()) for ext in supported_extensions):
                    # Get file extension
                    extension = '.' + filename.split('.')[-1].upper()
                    
                    output_files.append({
                        "filename": filename,
                        "key": key,
                        "format": extension,
                        "size": obj['Size'],
                        "version": file_version,
                        "last_modified": obj['LastModified'].isoformat(),
                        "download_url": None  # Will be generated on request
                    })
            
            # Sort by version (descending) if no specific version requested
            if not version:
                output_files.sort(key=lambda x: x.get('version', 0), reverse=True)
            
            logger.info(f"Found {len(output_files)} output files for project {project_name}" + 
                       (f" version {version}" if version else ""))
            return output_files
            
        except ClientError as e:
            logger.error(f"❌ S3 error checking output files: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error checking output files: {e}")
            return []
    
    async def list_project_files(self, project_name: str, version: int = None) -> List[Dict[str, Any]]:
        """
        Alias for check_output_files to maintain compatibility.
        List all output files for a project.
        """
        return await self.check_output_files(project_name, version)
    
    async def generate_download_url(self, project_name: str, filename: str, version: int = None, expiration: int = 3600) -> Optional[str]:
        """
        Generate a pre-signed URL for downloading an output file.
        Now supports versioned output folders.
        
        Args:
            project_name: Name of the project
            filename: Name of the file to download
            version: Version number for the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Pre-signed URL or None if error
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return None
        
        try:
            if version:
                key = f"output/{project_name}/v{version}/{filename}"
            else:
                # Try to find the file in the latest version
                output_files = await self.check_output_files(project_name)
                matching_files = [f for f in output_files if f['filename'] == filename]
                if not matching_files:
                    logger.warning(f"File not found: {filename} in project {project_name}")
                    return None
                key = matching_files[0]['key']
            
            # Check if file exists
            try:
                self.s3_client.head_object(Bucket=self.aws_bucket_name, Key=key)
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchKey':
                    logger.warning(f"File not found: {key}")
                    return None
                raise
            
            # Generate pre-signed URL with retry logic (always fresh)
            import time
            timestamp = int(time.time())
            
            try:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.aws_bucket_name, 
                        'Key': key,
                        'ResponseCacheControl': 'no-cache',  # Prevent caching
                        'ResponseExpires': f'timestamp-{timestamp}'  # Ensure uniqueness
                    },
                    ExpiresIn=expiration
                )
                
                logger.info(f"Generated fresh download URL for {filename} (expires in {expiration}s, ts: {timestamp})")
                logger.debug(f"Pre-signed URL: {url[:100]}...")  # Log first 100 chars for debugging
                return url
                
            except Exception as e:
                logger.error(f"Failed to generate pre-signed URL: {e}")
                # Retry once with fresh S3 client
                try:
                    self._init_s3_client()
                    url = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': self.aws_bucket_name, 'Key': key},
                        ExpiresIn=expiration
                    )
                    logger.info(f"Generated download URL on retry for {filename}")
                    return url
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
                    raise
            
        except ClientError as e:
            logger.error(f"❌ S3 error generating download URL: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error generating download URL: {e}")
            return None
    
    async def generate_script_hash(self, code: str) -> str:
        """Generate SHA256 hash of script content for metadata."""
        return hashlib.sha256(code.encode('utf-8')).hexdigest()
    
    async def create_version_metadata(self, project_name: str, version: int, 
                                    output_files: List[str], processing_time: float = None,
                                    worker_id: str = None, log_file: str = None) -> bool:
        """
        Create metadata.json for a processed version.
        
        Args:
            project_name: Name of the project
            version: Version number
            output_files: List of output filenames
            processing_time: Time taken to process (seconds)
            worker_id: ID of the worker that processed the script
            log_file: Name of the log file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return False
        
        try:
            # Get script content to generate hash
            script_content = await self.get_script_content(project_name, version)
            script_hash = await self.generate_script_hash(script_content) if script_content else None
            
            # Create metadata
            metadata = {
                "input_version": version,
                "project_name": project_name,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "processing_time": processing_time,
                "output_files": output_files,
                "script_hash": script_hash,
                "worker_id": worker_id or "unknown",
                "log_file": log_file,
                "metadata_version": "1.0"
            }
            
            # Upload metadata.json to versioned output folder
            key = f"output/{project_name}/v{version}/metadata.json"
            
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=key,
                Body=json.dumps(metadata, indent=2).encode('utf-8'),
                ContentType='application/json',
                ContentEncoding='utf-8'
            )
            
            logger.info(f"✅ Created metadata for {project_name} v{version}: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ S3 error creating metadata: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error creating metadata: {e}")
            return False
    
    async def get_version_metadata(self, project_name: str, version: int) -> Optional[Dict[str, Any]]:
        """
        Get metadata.json for a specific version.
        
        Args:
            project_name: Name of the project
            version: Version number
            
        Returns:
            Metadata dictionary or None if not found
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return None
        
        try:
            key = f"output/{project_name}/v{version}/metadata.json"
            
            response = self.s3_client.get_object(
                Bucket=self.aws_bucket_name,
                Key=key
            )
            
            content = response['Body'].read().decode('utf-8')
            metadata = json.loads(content)
            
            logger.info(f"✅ Retrieved metadata for {project_name} v{version}")
            return metadata
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Metadata not found for {project_name} v{version}")
            else:
                logger.error(f"❌ S3 error getting metadata: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting metadata: {e}")
            return None
    
    async def mark_script_processed(self, project_name: str, version: int, 
                                  output_files: List[str] = None, processing_time: float = None,
                                  worker_id: str = None, log_file: str = None) -> bool:
        """
        Mark a script as processed by creating a .done file and metadata.
        Now supports versioned output correlation.
        
        Args:
            project_name: Name of the project
            version: Version number that was processed
            output_files: List of output filenames
            processing_time: Time taken to process (seconds)
            worker_id: ID of the worker that processed the script
            log_file: Name of the log file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return False
        
        try:
            # Create metadata.json if output files are provided
            if output_files:
                await self.create_version_metadata(
                    project_name, version, output_files, 
                    processing_time, worker_id, log_file
                )
            
            # Create .done file with enhanced metadata
            key = f"processed/{project_name}/{project_name}_v{version}.py.done"
            
            metadata = {
                "project_id": project_name,
                "version": str(version),
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "service": "cadscribe-freecad",
                "output_files_count": str(len(output_files)) if output_files else "0",
                "processing_time": str(processing_time) if processing_time else "unknown",
                "worker_id": worker_id or "unknown"
            }
            
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=key,
                Body=b'',
                Metadata=metadata
            )
            
            logger.info(f"✅ Marked script as processed: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ S3 error marking script processed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error marking script processed: {e}")
            return False
    
    async def get_project_logs(self, project_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent log files for a project.
        
        Args:
            project_name: Name of the project
            limit: Maximum number of log files to return
            
        Returns:
            List of log file information
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return []
        
        try:
            prefix = f"logs/{project_name}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.aws_bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            log_files = []
            log_pattern = re.compile(rf"{re.escape(project_name)}_info_(\d{{8}}_\d{{6}})\.log$")
            
            for obj in response['Contents']:
                key = obj['Key']
                filename = key.split('/')[-1]
                match = log_pattern.search(filename)
                if match:
                    timestamp_str = match.group(1)
                    
                    log_files.append({
                        "filename": filename,
                        "key": key,
                        "timestamp": timestamp_str,
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat()
                    })
            
            # Sort by timestamp (most recent first)
            log_files.sort(key=lambda x: x['timestamp'], reverse=True)
            return log_files[:limit]
            
        except ClientError as e:
            logger.error(f"❌ S3 error getting project logs: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting project logs: {e}")
            return []
    
    async def get_log_content(self, project_name: str, log_filename: str) -> Optional[str]:
        """
        Get the content of a specific log file.
        
        Args:
            project_name: Name of the project
            log_filename: Name of the log file
            
        Returns:
            Log content as string, or None if not found
        """
        if not self.s3_client or not self.aws_bucket_name:
            logger.warning("S3 not configured")
            return None
        
        try:
            key = f"logs/{project_name}/{log_filename}"
            
            response = self.s3_client.get_object(
                Bucket=self.aws_bucket_name,
                Key=key
            )
            
            content = response['Body'].read().decode('utf-8')
            logger.info(f"✅ Retrieved log content: {key}")
            return content
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Log file not found: {key}")
            else:
                logger.error(f"❌ S3 error getting log: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting log content: {e}")
            return None
    
    async def auto_fix_failed_script(self, project_name: str, version: int, 
                                    error_message: str = None, log_file: str = None) -> bool:
        """
        Automatically replace a failed script with a corrected FreeCAD version.
        This prevents the EC2 worker from getting stuck in processing loops.
        
        Args:
            project_name: Name of the project
            version: Version number that failed
            error_message: Error description (optional)
            log_file: Specific log file to analyze (optional)
            
        Returns:
            True if script was auto-fixed, False otherwise
        """
        try:
            if not self.s3_client:
                logger.error("❌ S3 client not initialized")
                return False
            
            # Get the original broken script
            script_key = f"input/{project_name}/{project_name}_v{version}.py"
            
            try:
                response = self.s3_client.get_object(
                    Bucket=self.aws_bucket_name,
                    Key=script_key
                )
                original_code = response['Body'].read().decode('utf-8')
            except ClientError:
                logger.error(f"❌ Could not retrieve original script: {script_key}")
                return False
            
            # Get detailed error information from log files
            detailed_error_info = await self._analyze_error_logs(project_name, version, log_file)
            
            # Use AI to generate intelligent fix based on logs and original code
            corrected_code = await self._generate_ai_fixed_script(
                original_code, 
                detailed_error_info, 
                error_message
            )
            
            # Replace the broken script with corrected version
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=script_key,
                Body=corrected_code,
                ContentType='text/plain',
                Metadata={
                    'auto_fixed': 'true',
                    'original_error': error_message,
                    'fixed_at': datetime.now(timezone.utc).isoformat(),
                    'fix_type': 'cadquery_to_freecad'
                }
            )
            
            # Remove processed marker so EC2 worker will reprocess
            processed_key = f"processed/{project_name}/{project_name}_v{version}.py.done"
            try:
                self.s3_client.delete_object(
                    Bucket=self.aws_bucket_name,
                    Key=processed_key
                )
                logger.info(f"🗑️ Removed processed marker: {processed_key}")
            except ClientError:
                pass  # Marker might not exist
            
            # Clear any existing output files
            await self._clear_version_outputs(project_name, version)
            
            # Log the auto-fix
            fix_log = {
                "project_name": project_name,
                "version": version,
                "action": "auto_fix",
                "original_error": error_message,
                "fixed_at": datetime.now(timezone.utc).isoformat(),
                "fix_type": "cadquery_to_freecad",
                "status": "script_replaced"
            }
            
            fix_log_key = f"logs/{project_name}/{project_name}_autofix_v{version}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=fix_log_key,
                Body=json.dumps(fix_log, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"✅ Auto-fixed script: {project_name} v{version} - EC2 loop prevented")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error auto-fixing script: {e}")
            return False
    
    def _generate_freecad_replacement(self, original_code: str, error_message: str) -> str:
        """Generate a corrected FreeCAD script to replace broken code."""
        
        # If the error is related to CadQuery imports, create a FreeCAD equivalent
        if 'cadquery' in error_message.lower() or 'cq' in error_message.lower():
            logger.info("🔧 Generating FreeCAD replacement for CadQuery script")
            
            # Try to extract dimensions from original code
            dimensions = self._extract_dimensions_from_code(original_code)
            
            # Determine shape type from original code
            if '.box(' in original_code or 'box' in original_code.lower():
                return self._generate_freecad_box(dimensions)
            elif '.cylinder(' in original_code or 'cylinder' in original_code.lower():
                return self._generate_freecad_cylinder(dimensions)
            elif '.sphere(' in original_code or 'sphere' in original_code.lower():
                return self._generate_freecad_sphere(dimensions)
            else:
                # Default to a simple cube
                return self._generate_freecad_box([10, 10, 10])
        
        # For other errors, create a default FreeCAD cube
        logger.info("🔧 Generating default FreeCAD cube for failed script")
        return self._generate_freecad_box([10, 10, 10])
    
    async def _analyze_error_logs(self, project_name: str, version: int, specific_log_file: str = None) -> dict:
        """Analyze error logs from S3 to get detailed error information."""
        try:
            error_info = {
                "error_type": "unknown",
                "error_details": "",
                "stack_trace": "",
                "missing_modules": [],
                "syntax_errors": [],
                "runtime_errors": []
            }
            
            # If specific log file provided, use it
            if specific_log_file:
                log_content = await self.get_log_content(project_name, specific_log_file)
                if log_content:
                    error_info = self._parse_log_content(log_content)
                    logger.info(f"📋 Analyzed specific log file: {specific_log_file}")
                    return error_info
            
            # Otherwise, get recent log files for this project
            recent_logs = await self.get_project_logs(project_name, limit=5)
            
            for log_entry in recent_logs:
                log_filename = log_entry.get("filename", "")
                
                # Look for logs related to this version
                if f"v{version}" in log_filename or f"_{version}_" in log_filename:
                    log_content = await self.get_log_content(project_name, log_filename)
                    if log_content:
                        parsed_info = self._parse_log_content(log_content)
                        # Merge error information
                        error_info.update(parsed_info)
                        logger.info(f"📋 Analyzed log file: {log_filename}")
                        break
            
            return error_info
            
        except Exception as e:
            logger.error(f"❌ Error analyzing logs: {e}")
            return {"error_type": "log_analysis_failed", "error_details": str(e)}
    
    def _parse_log_content(self, log_content: str) -> dict:
        """Parse log content to extract error information."""
        error_info = {
            "error_type": "unknown",
            "error_details": "",
            "stack_trace": "",
            "missing_modules": [],
            "syntax_errors": [],
            "runtime_errors": []
        }
        
        lines = log_content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for import errors
            if 'importerror' in line_lower or 'modulenotfounderror' in line_lower:
                error_info["error_type"] = "import_error"
                error_info["error_details"] = line.strip()
                
                # Extract module name
                if 'cadquery' in line_lower:
                    error_info["missing_modules"].append("cadquery")
                elif 'cq' in line_lower:
                    error_info["missing_modules"].append("cadquery")
                elif 'importgui' in line_lower:
                    error_info["missing_modules"].append("importgui")
                
            # Check for GUI-related errors
            elif 'importgui' in line_lower or 'gui' in line_lower:
                error_info["error_type"] = "gui_error"
                error_info["error_details"] = line.strip()
                error_info["missing_modules"].append("importgui")
                
            # Check for syntax errors
            elif 'syntaxerror' in line_lower:
                error_info["error_type"] = "syntax_error"
                error_info["syntax_errors"].append(line.strip())
                
            # Check for attribute errors (common with wrong module usage)
            elif 'attributeerror' in line_lower:
                error_info["error_type"] = "attribute_error"
                error_info["runtime_errors"].append(line.strip())
                
            # Check for runtime errors
            elif 'error:' in line_lower or 'exception:' in line_lower:
                error_info["runtime_errors"].append(line.strip())
                
            # Check for FreeCAD specific errors
            elif 'freecad' in line_lower and ('error' in line_lower or 'exception' in line_lower):
                error_info["error_type"] = "freecad_error"
                error_info["runtime_errors"].append(line.strip())
                
            # Capture stack trace
            elif 'traceback' in line_lower:
                # Get next few lines for stack trace
                stack_lines = []
                for j in range(i, min(i + 10, len(lines))):
                    if lines[j].strip():
                        stack_lines.append(lines[j])
                    else:
                        break
                error_info["stack_trace"] = '\n'.join(stack_lines)
        
        return error_info
    
    async def _generate_ai_fixed_script(self, original_code: str, error_info: dict, error_message: str = None) -> str:
        """Use AI to generate a fixed script based on error analysis."""
        try:
            # Import AI service here to avoid circular imports
            from services.ai_service import ai_service
            
            # Create detailed prompt for AI to fix the script
            fix_prompt = self._create_fix_prompt(original_code, error_info, error_message)
            
            # Use AI to generate fixed code
            fixed_code = await ai_service.generate_code_fix(fix_prompt)
            
            if fixed_code and 'import FreeCAD' in fixed_code:
                logger.info("🤖 AI generated intelligent fix")
                return fixed_code
            else:
                logger.warning("🤖 AI fix failed, using fallback")
                # Fallback to rule-based fix
                return self._generate_freecad_replacement(original_code, error_message or "AI fix failed")
                
        except Exception as e:
            logger.error(f"❌ AI fix generation failed: {e}")
            # Fallback to rule-based fix
            return self._generate_freecad_replacement(original_code, error_message or "AI fix failed")
    
    def _create_fix_prompt(self, original_code: str, error_info: dict, error_message: str = None) -> str:
        """Create a detailed prompt for AI to fix the script."""
        
        prompt = f"""Fix this broken Python script to work with FreeCAD HEADLESS (command line only).

ORIGINAL BROKEN CODE:
```python
{original_code}
```

ERROR ANALYSIS:
- Error Type: {error_info.get('error_type', 'unknown')}
- Error Details: {error_info.get('error_details', 'No details')}
- Missing Modules: {', '.join(error_info.get('missing_modules', []))}
- Syntax Errors: {'; '.join(error_info.get('syntax_errors', []))}
- Runtime Errors: {'; '.join(error_info.get('runtime_errors', []))}

REQUIREMENTS FOR FIXED CODE:
1. Use ONLY FreeCAD imports for HEADLESS mode: import FreeCAD, Part, Mesh, os
2. DO NOT use ImportGui or any GUI components - this runs in command line only
3. Create FreeCAD document: doc = FreeCAD.newDocument("MyDoc")
4. Use FreeCAD Part workbench objects (Part::Box, Part::Cylinder, etc.)
5. Include doc.recompute() after creating objects
6. MUST include multi-format export code at the end

REQUIRED EXPORT TEMPLATE (HEADLESS):
```python
# Multi-format export (HEADLESS - no GUI)
output_dir = os.environ.get("FREECAD_OUTPUT", "/tmp")
base_name = "MyHeadlessModel"

try:
    # Save FreeCAD document
    fcstd_path = os.path.join(output_dir, f"{{base_name}}.fcstd")
    doc.saveAs(fcstd_path)
    
    # Export STL mesh
    stl_path = os.path.join(output_dir, f"{{base_name}}.stl")
    Mesh.export([object_name], stl_path)
    
    # Export OBJ mesh
    obj_path = os.path.join(output_dir, f"{{base_name}}.obj")
    Mesh.export([object_name], obj_path)
    
    # Export STEP (using Part module directly)
    step_path = os.path.join(output_dir, f"{{base_name}}.step")
    Part.export([object_name], step_path)
    
    # Export IGES (alternative to GLTF for CAD)
    iges_path = os.path.join(output_dir, f"{{base_name}}.iges")
    Part.export([object_name], iges_path)
    
except Exception as e:
    print(f"Export error: {{e}}")
```

Generate ONLY the corrected Python code, no explanations."""
        
        return prompt
    
    def _extract_dimensions_from_code(self, code: str) -> list:
        """Extract numeric dimensions from code."""
        import re
        
        # Look for numeric values in the code
        numbers = re.findall(r'\b\d+\.?\d*\b', code)
        
        if len(numbers) >= 3:
            try:
                return [float(numbers[0]), float(numbers[1]), float(numbers[2])]
            except ValueError:
                pass
        
        # Default dimensions
        return [10, 10, 10]
    
    def _generate_freecad_box(self, dimensions: list) -> str:
        """Generate FreeCAD box script."""
        w, h, d = dimensions[:3] if len(dimensions) >= 3 else [10, 10, 10]
        
        return f'''import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
cube = doc.addObject("Part::Box", "Cube")
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
    print(f"Export error: {{e}}")'''
    
    def _generate_freecad_cylinder(self, dimensions: list) -> str:
        """Generate FreeCAD cylinder script."""
        r, h = dimensions[:2] if len(dimensions) >= 2 else [5, 10]
        
        return f'''import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
cylinder = doc.addObject("Part::Cylinder", "Cylinder")
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
    print(f"Export error: {{e}}")'''
    
    def _generate_freecad_sphere(self, dimensions: list) -> str:
        """Generate FreeCAD sphere script."""
        r = dimensions[0] if len(dimensions) >= 1 else 5
        
        return f'''import FreeCAD, Part, Mesh
import os

doc = FreeCAD.newDocument("MyDoc")
sphere = doc.addObject("Part::Sphere", "Sphere")
sphere.Radius = {r}
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

    async def mark_script_failed(self, project_name: str, version: int, 
                                error_message: str, retry_count: int = 0) -> bool:
        """
        Mark a script as failed and store error information.
        
        Args:
            project_name: Name of the project
            version: Version number that failed
            error_message: Error description
            retry_count: Number of retries attempted
            
        Returns:
            True if marked successfully, False otherwise
        """
        try:
            if not self.s3_client:
                logger.error("❌ S3 client not initialized")
                return False
            
            # Create error metadata
            error_data = {
                "project_name": project_name,
                "version": version,
                "status": "FAILED",
                "error_message": error_message,
                "retry_count": retry_count,
                "failed_at": datetime.now(timezone.utc).isoformat(),
                "max_retries": 3,  # Maximum retry attempts
                "next_retry_after": datetime.now(timezone.utc).isoformat() if retry_count < 3 else None
            }
            
            # Store error metadata
            error_key = f"errors/{project_name}/{project_name}_v{version}_error.json"
            
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=error_key,
                Body=json.dumps(error_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"✅ Marked script as failed: {project_name} v{version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking script failed: {e}")
            return False
    
    async def replace_failed_script(self, project_name: str, version: int, 
                                  new_code: str, user_id: str = None) -> Dict[str, Any]:
        """
        Replace a failed script with a corrected version.
        
        Args:
            project_name: Name of the project
            version: Version number to replace
            new_code: Corrected Python script
            user_id: User ID for tracking
            
        Returns:
            Dictionary with replacement status and details
        """
        try:
            if not self.s3_client:
                logger.error("❌ S3 client not initialized")
                return {"success": False, "error": "S3 not configured"}
            
            # Check if there's an error record for this version
            error_key = f"errors/{project_name}/{project_name}_v{version}_error.json"
            
            try:
                error_response = self.s3_client.get_object(
                    Bucket=self.aws_bucket_name,
                    Key=error_key
                )
                error_data = json.loads(error_response['Body'].read().decode('utf-8'))
                logger.info(f"📋 Found error record for {project_name} v{version}")
            except ClientError:
                logger.warning(f"⚠️ No error record found for {project_name} v{version}")
                error_data = None
            
            # Replace the script file
            script_key = f"input/{project_name}/{project_name}_v{version}.py"
            
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=script_key,
                Body=new_code,
                ContentType='text/plain',
                Metadata={
                    'user_id': user_id or 'system',
                    'replaced_at': datetime.now(timezone.utc).isoformat(),
                    'original_error': error_data.get('error_message', 'Unknown') if error_data else 'Manual replacement'
                }
            )
            
            # Remove processed marker if it exists
            processed_key = f"processed/{project_name}/{project_name}_v{version}.py.done"
            try:
                self.s3_client.delete_object(
                    Bucket=self.aws_bucket_name,
                    Key=processed_key
                )
                logger.info(f"🗑️ Removed processed marker for {project_name} v{version}")
            except ClientError:
                pass  # Marker might not exist
            
            # Remove error record
            if error_data:
                try:
                    self.s3_client.delete_object(
                        Bucket=self.aws_bucket_name,
                        Key=error_key
                    )
                    logger.info(f"🗑️ Removed error record for {project_name} v{version}")
                except ClientError:
                    pass
            
            # Clear any existing output files for this version
            await self._clear_version_outputs(project_name, version)
            
            logger.info(f"✅ Successfully replaced script: {project_name} v{version}")
            
            return {
                "success": True,
                "project_name": project_name,
                "version": version,
                "script_key": script_key,
                "replaced_at": datetime.now(timezone.utc).isoformat(),
                "message": "Script replaced successfully. AWS worker will reprocess it."
            }
            
        except Exception as e:
            logger.error(f"❌ Error replacing failed script: {e}")
            return {"success": False, "error": str(e)}
    
    async def _clear_version_outputs(self, project_name: str, version: int) -> bool:
        """Clear all output files for a specific version."""
        try:
            if not self.s3_client:
                return False
            
            # List all files in the version output folder
            output_prefix = f"output/{project_name}/v{version}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.aws_bucket_name,
                Prefix=output_prefix
            )
            
            if 'Contents' in response:
                # Delete all files in the version folder
                objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                
                if objects_to_delete:
                    self.s3_client.delete_objects(
                        Bucket=self.aws_bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    logger.info(f"🗑️ Cleared {len(objects_to_delete)} output files for {project_name} v{version}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing version outputs: {e}")
            return False
    
    async def get_failed_scripts(self, project_name: str = None) -> List[Dict[str, Any]]:
        """
        Get list of failed scripts, optionally filtered by project.
        
        Args:
            project_name: Optional project name filter
            
        Returns:
            List of failed script information
        """
        try:
            if not self.s3_client:
                logger.error("❌ S3 client not initialized")
                return []
            
            # List error files
            prefix = f"errors/{project_name}/" if project_name else "errors/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.aws_bucket_name,
                Prefix=prefix
            )
            
            failed_scripts = []
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('_error.json'):
                        try:
                            # Get error details
                            error_response = self.s3_client.get_object(
                                Bucket=self.aws_bucket_name,
                                Key=obj['Key']
                            )
                            error_data = json.loads(error_response['Body'].read().decode('utf-8'))
                            
                            failed_scripts.append({
                                "project_name": error_data.get("project_name"),
                                "version": error_data.get("version"),
                                "error_message": error_data.get("error_message"),
                                "retry_count": error_data.get("retry_count", 0),
                                "failed_at": error_data.get("failed_at"),
                                "can_retry": error_data.get("retry_count", 0) < 3,
                                "error_file": obj['Key']
                            })
                            
                        except Exception as e:
                            logger.error(f"❌ Error reading error file {obj['Key']}: {e}")
                            continue
            
            return failed_scripts
            
        except Exception as e:
            logger.error(f"❌ Error getting failed scripts: {e}")
            return []
    
    async def retry_failed_script(self, project_name: str, version: int) -> Dict[str, Any]:
        """
        Retry processing a failed script by removing processed marker and error record.
        
        Args:
            project_name: Name of the project
            version: Version number to retry
            
        Returns:
            Dictionary with retry status
        """
        try:
            if not self.s3_client:
                logger.error("❌ S3 client not initialized")
                return {"success": False, "error": "S3 not configured"}
            
            # Get current error data
            error_key = f"errors/{project_name}/{project_name}_v{version}_error.json"
            
            try:
                error_response = self.s3_client.get_object(
                    Bucket=self.aws_bucket_name,
                    Key=error_key
                )
                error_data = json.loads(error_response['Body'].read().decode('utf-8'))
                
                # Check retry limit
                retry_count = error_data.get("retry_count", 0)
                if retry_count >= 3:
                    return {
                        "success": False, 
                        "error": "Maximum retry attempts reached",
                        "retry_count": retry_count
                    }
                
            except ClientError:
                return {"success": False, "error": "No error record found"}
            
            # Remove processed marker
            processed_key = f"processed/{project_name}/{project_name}_v{version}.py.done"
            try:
                self.s3_client.delete_object(
                    Bucket=self.aws_bucket_name,
                    Key=processed_key
                )
                logger.info(f"🗑️ Removed processed marker for retry: {project_name} v{version}")
            except ClientError:
                pass  # Marker might not exist
            
            # Update error record with incremented retry count
            error_data["retry_count"] = retry_count + 1
            error_data["retry_attempted_at"] = datetime.now(timezone.utc).isoformat()
            
            self.s3_client.put_object(
                Bucket=self.aws_bucket_name,
                Key=error_key,
                Body=json.dumps(error_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"🔄 Initiated retry for {project_name} v{version} (attempt {retry_count + 1})")
            
            return {
                "success": True,
                "project_name": project_name,
                "version": version,
                "retry_count": retry_count + 1,
                "message": "Retry initiated. AWS worker will reprocess the script."
            }
            
        except Exception as e:
            logger.error(f"❌ Error retrying failed script: {e}")
            return {"success": False, "error": str(e)}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        return {
            "s3_operations": self.performance_metrics,
            "bucket_name": self.aws_bucket_name,
            "region": self.aws_region,
            "configured": self.s3_client is not None
        }


# Global S3 service instance
s3_service = S3Service()
