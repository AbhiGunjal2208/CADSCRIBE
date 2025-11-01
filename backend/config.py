"""
Configuration settings for the CADSCRIBE backend.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # Database
        self.mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/cadscribe")
        self.database_name: str = os.getenv("DATABASE_NAME", "cadscribe")
        
        # API Keys
        self.openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        
        # AWS Configuration
        self.aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_bucket_name: Optional[str] = os.getenv("AWS_BUCKET_NAME")
        self.aws_region: str = os.getenv("AWS_REGION", "us-east-1")
        
        # Service URLs
        self.cad_service_url: str = os.getenv("CAD_SERVICE_URL", "http://localhost:9000")
        
        # Security
        self.secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm: str = "HS256"
        self.access_token_expire_minutes: int = 30
        
        # CORS
        self.cors_origins: list = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ]
        
        # File Storage
        self.upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
        self.generated_models_dir: str = os.getenv("GENERATED_MODELS_DIR", "generated_models")
        
        # Debug mode
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"


# Global settings instance
settings = Settings()
