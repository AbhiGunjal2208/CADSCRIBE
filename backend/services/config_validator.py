"""
Configuration validation service for CADSCRIBE backend.
Validates all required environment variables and service configurations.
"""
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a configuration validation check."""
    service: str
    status: str  # 'valid', 'warning', 'error', 'not_configured'
    message: str
    details: Optional[Dict[str, Any]] = None


class ConfigValidator:
    """Validates system configuration and service connectivity."""
    
    def __init__(self):
        """Initialize the configuration validator."""
        self.results: List[ValidationResult] = []
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all system configurations.
        
        Returns:
            Dict containing validation results and overall status
        """
        self.results = []
        
        # Validate each service
        self._validate_environment_variables()
        self._validate_mongodb()
        self._validate_aws_s3()
        self._validate_ai_services()
        self._validate_cad_service()
        
        # Determine overall status
        error_count = sum(1 for r in self.results if r.status == 'error')
        warning_count = sum(1 for r in self.results if r.status == 'warning')
        
        if error_count > 0:
            overall_status = 'error'
            overall_message = f"Configuration has {error_count} errors and {warning_count} warnings"
        elif warning_count > 0:
            overall_status = 'warning'
            overall_message = f"Configuration has {warning_count} warnings"
        else:
            overall_status = 'valid'
            overall_message = "All configurations are valid"
        
        return {
            'overall_status': overall_status,
            'overall_message': overall_message,
            'error_count': error_count,
            'warning_count': warning_count,
            'total_checks': len(self.results),
            'results': [
                {
                    'service': r.service,
                    'status': r.status,
                    'message': r.message,
                    'details': r.details
                }
                for r in self.results
            ]
        }
    
    def _validate_environment_variables(self):
        """Validate required environment variables."""
        required_vars = [
            'SECRET_KEY',
            'MONGODB_URI',
            'DATABASE_NAME'
        ]
        
        optional_vars = [
            'DEBUG',
            'CORS_ORIGINS',
            'ACCESS_TOKEN_EXPIRE_MINUTES'
        ]
        
        missing_required = []
        missing_optional = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)
        
        if missing_required:
            self.results.append(ValidationResult(
                service='environment',
                status='error',
                message=f"Missing required environment variables: {', '.join(missing_required)}",
                details={'missing_required': missing_required, 'missing_optional': missing_optional}
            ))
        elif missing_optional:
            self.results.append(ValidationResult(
                service='environment',
                status='warning',
                message=f"Missing optional environment variables: {', '.join(missing_optional)}",
                details={'missing_optional': missing_optional}
            ))
        else:
            self.results.append(ValidationResult(
                service='environment',
                status='valid',
                message="All environment variables are configured"
            ))
    
    def _validate_mongodb(self):
        """Validate MongoDB configuration and connectivity."""
        mongodb_uri = os.getenv('MONGODB_URI')
        database_name = os.getenv('DATABASE_NAME', 'cadscribe')
        
        if not mongodb_uri:
            self.results.append(ValidationResult(
                service='mongodb',
                status='error',
                message="MONGODB_URI not configured"
            ))
            return
        
        try:
            # Test connection
            client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test ping
            client.admin.command('ping')
            
            # Test database access
            db = client[database_name]
            collections = db.list_collection_names()
            
            self.results.append(ValidationResult(
                service='mongodb',
                status='valid',
                message=f"MongoDB connection successful to database '{database_name}'",
                details={
                    'database_name': database_name,
                    'collections_count': len(collections),
                    'collections': collections[:5]  # First 5 collections
                }
            ))
            
            client.close()
            
        except ServerSelectionTimeoutError:
            self.results.append(ValidationResult(
                service='mongodb',
                status='error',
                message="MongoDB server selection timeout - server may be down or unreachable",
                details={'mongodb_uri': mongodb_uri[:20] + '...' if len(mongodb_uri) > 20 else mongodb_uri}
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                service='mongodb',
                status='error',
                message=f"MongoDB connection failed: {str(e)}",
                details={'error_type': type(e).__name__}
            ))
    
    def _validate_aws_s3(self):
        """Validate AWS S3 configuration and connectivity."""
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_bucket_name = os.getenv('AWS_BUCKET_NAME')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not all([aws_access_key_id, aws_secret_access_key, aws_bucket_name]):
            missing = []
            if not aws_access_key_id:
                missing.append('AWS_ACCESS_KEY_ID')
            if not aws_secret_access_key:
                missing.append('AWS_SECRET_ACCESS_KEY')
            if not aws_bucket_name:
                missing.append('AWS_BUCKET_NAME')
            
            self.results.append(ValidationResult(
                service='aws_s3',
                status='warning',
                message=f"AWS S3 not fully configured. Missing: {', '.join(missing)}",
                details={'missing_variables': missing}
            ))
            return
        
        try:
            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )
            
            # Test bucket access
            s3_client.head_bucket(Bucket=aws_bucket_name)
            
            # Test list objects (limited)
            response = s3_client.list_objects_v2(
                Bucket=aws_bucket_name,
                MaxKeys=1
            )
            
            # Check bucket structure
            prefixes = ['input/', 'output/', 'logs/', 'processed/']
            existing_prefixes = []
            
            for prefix in prefixes:
                try:
                    response = s3_client.list_objects_v2(
                        Bucket=aws_bucket_name,
                        Prefix=prefix,
                        MaxKeys=1
                    )
                    if 'Contents' in response:
                        existing_prefixes.append(prefix)
                except:
                    pass
            
            self.results.append(ValidationResult(
                service='aws_s3',
                status='valid',
                message=f"AWS S3 connection successful to bucket '{aws_bucket_name}'",
                details={
                    'bucket_name': aws_bucket_name,
                    'region': aws_region,
                    'existing_prefixes': existing_prefixes,
                    'expected_prefixes': prefixes
                }
            ))
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                self.results.append(ValidationResult(
                    service='aws_s3',
                    status='error',
                    message=f"S3 bucket '{aws_bucket_name}' does not exist",
                    details={'bucket_name': aws_bucket_name, 'error_code': error_code}
                ))
            elif error_code == 'AccessDenied':
                self.results.append(ValidationResult(
                    service='aws_s3',
                    status='error',
                    message=f"Access denied to S3 bucket '{aws_bucket_name}' - check IAM permissions",
                    details={'bucket_name': aws_bucket_name, 'error_code': error_code}
                ))
            else:
                self.results.append(ValidationResult(
                    service='aws_s3',
                    status='error',
                    message=f"S3 error: {e.response['Error']['Message']}",
                    details={'error_code': error_code}
                ))
        except NoCredentialsError:
            self.results.append(ValidationResult(
                service='aws_s3',
                status='error',
                message="AWS credentials not found or invalid"
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                service='aws_s3',
                status='error',
                message=f"S3 validation failed: {str(e)}",
                details={'error_type': type(e).__name__}
            ))
    
    def _validate_ai_services(self):
        """Validate AI service configurations."""
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        
        ai_services = []
        
        if gemini_api_key:
            ai_services.append('Gemini')
        if openrouter_api_key:
            ai_services.append('OpenRouter')
        
        if not ai_services:
            self.results.append(ValidationResult(
                service='ai_services',
                status='error',
                message="No AI services configured. Need at least GEMINI_API_KEY or OPENROUTER_API_KEY",
                details={'configured_services': []}
            ))
        elif len(ai_services) == 1:
            self.results.append(ValidationResult(
                service='ai_services',
                status='warning',
                message=f"Only {ai_services[0]} configured. Consider adding backup AI service",
                details={'configured_services': ai_services}
            ))
        else:
            self.results.append(ValidationResult(
                service='ai_services',
                status='valid',
                message=f"AI services configured: {', '.join(ai_services)}",
                details={'configured_services': ai_services}
            ))
    
    def _validate_cad_service(self):
        """Validate CAD service configuration."""
        cad_service_url = os.getenv('CAD_SERVICE_URL')
        
        if not cad_service_url:
            self.results.append(ValidationResult(
                service='cad_service',
                status='warning',
                message="CAD_SERVICE_URL not configured - CAD processing may not work",
                details={'default_url': 'http://localhost:9000'}
            ))
        else:
            # Basic URL validation
            if not (cad_service_url.startswith('http://') or cad_service_url.startswith('https://')):
                self.results.append(ValidationResult(
                    service='cad_service',
                    status='error',
                    message=f"Invalid CAD service URL format: {cad_service_url}",
                    details={'url': cad_service_url}
                ))
            else:
                self.results.append(ValidationResult(
                    service='cad_service',
                    status='valid',
                    message=f"CAD service URL configured: {cad_service_url}",
                    details={'url': cad_service_url}
                ))
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration status."""
        return {
            'environment_variables': {
                'SECRET_KEY': '✓' if os.getenv('SECRET_KEY') else '✗',
                'MONGODB_URI': '✓' if os.getenv('MONGODB_URI') else '✗',
                'DATABASE_NAME': '✓' if os.getenv('DATABASE_NAME') else '✗',
                'DEBUG': '✓' if os.getenv('DEBUG') else '○',
                'CORS_ORIGINS': '✓' if os.getenv('CORS_ORIGINS') else '○'
            },
            'ai_services': {
                'GEMINI_API_KEY': '✓' if os.getenv('GEMINI_API_KEY') else '✗',
                'OPENROUTER_API_KEY': '✓' if os.getenv('OPENROUTER_API_KEY') else '✗'
            },
            'aws_s3': {
                'AWS_ACCESS_KEY_ID': '✓' if os.getenv('AWS_ACCESS_KEY_ID') else '✗',
                'AWS_SECRET_ACCESS_KEY': '✓' if os.getenv('AWS_SECRET_ACCESS_KEY') else '✗',
                'AWS_BUCKET_NAME': '✓' if os.getenv('AWS_BUCKET_NAME') else '✗',
                'AWS_REGION': '✓' if os.getenv('AWS_REGION') else '○'
            },
            'cad_service': {
                'CAD_SERVICE_URL': '✓' if os.getenv('CAD_SERVICE_URL') else '○'
            },
            'legend': {
                '✓': 'Configured',
                '✗': 'Missing/Required',
                '○': 'Optional/Default'
            }
        }


# Global validator instance
config_validator = ConfigValidator()
