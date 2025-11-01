"""MongoDB schema models and type hints for the application."""
from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
from datetime import timezone

class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class FileType(str, Enum):
    """File type enumeration."""
    INPUT = "input"
    OUTPUT = "output"
    LOG = "log"
    PROCESSED = "processed"

class ModelFormat(str, Enum):
    """CAD model file formats."""
    STL = "stl"
    STEP = "step"
    OBJ = "obj"
    FCSTD = "fcstd"
    
    @classmethod
    def validate(cls, value: str) -> bool:
        """Validate if the given value is a valid format."""
        return value.lower() in cls._value2member_map_

class BaseDocument(TypedDict):
    """Base document with common fields."""
    created_at: datetime
    updated_at: datetime

class UserPreferences(TypedDict, total=False):
    """User preferences dictionary."""
    theme: str
    language: str
    notifications_enabled: bool
    default_file_format: str

class User(BaseDocument):
    """User document schema."""
    email: str
    name: str
    password_hash: str
    preferences: UserPreferences

class ProjectMetadata(TypedDict, total=False):
    """Project metadata dictionary."""
    description: str
    confidence: float
    generation_time: float
    parameters: Dict[str, Any]

class Project(BaseDocument):
    """Project document schema - root document for all project data."""
    project_id: str  # Unique project identifier
    project_name: str
    created_by: str  # User ID who created the project
    current_version: int
    ai_model_used: Optional[str]
    status: ProjectStatus
    latest_s3_input: Optional[str]
    latest_s3_output: List[str]
    metadata: ProjectMetadata

class MessageMetadata(TypedDict, total=False):
    """Message metadata dictionary."""
    source_model: str
    confidence: float
    response_time: float
    s3_url: str
    version: int
    error: str

class Message(BaseDocument):
    """Chat message document schema - linked to projects."""
    project_id: str
    user_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: MessageMetadata

class FileMetadata(TypedDict, total=False):
    """File metadata dictionary."""
    file_name: str
    ai_model: str
    uploaded_by: str
    generated_by: str
    file_size: int
    content_type: str

class File(BaseDocument):
    """File document schema - tracks all project files."""
    project_id: str
    version: int
    file_type: FileType
    s3_path: str
    timestamp: datetime
    metadata: FileMetadata

class Log(BaseDocument):
    """Log document schema - stores worker execution logs."""
    project_id: str
    version: int
    s3_log_path: str
    log_summary: str
    timestamp: datetime
    metadata: Dict[str, Any]

# Legacy schemas for migration
class LegacyChatMessage(BaseDocument):
    """Legacy chat message document schema."""
    user_id: str
    project_id: Optional[str]
    content: str
    role: Literal['user', 'assistant']
    metadata: Dict[str, Any]

# Collection indexes configuration
INDEXES = {
    "users": [
        [("email", 1)],  # Unique index on email
        [("created_at", 1)]
    ],
    "projects": [
        [("project_id", 1)],  # Unique index on project_id
        [("created_by", 1)],  # Index on created_by for user's projects
        [("updated_at", -1)],  # Descending index on updated_at for latest first
        [("created_by", 1), ("updated_at", -1)]  # Compound index for user's projects by date
    ],
    "messages": [
        [("project_id", 1)],  # Index on project_id for faster message lookups
        [("timestamp", 1)],  # Index on timestamp for chronological order
        [("project_id", 1), ("timestamp", 1)],  # Compound index for ordered chat history
        [("user_id", 1)]  # Index on user_id
    ],
    "files": [
        [("project_id", 1)],  # Index on project_id for project files
        [("version", 1)],  # Index on version
        [("file_type", 1)],  # Index on file_type
        [("project_id", 1), ("version", -1)],  # Compound index for project files by version
        [("project_id", 1), ("file_type", 1)]  # Compound index for project files by type
    ],
    "logs": [
        [("project_id", 1)],  # Index on project_id for project logs
        [("version", 1)],  # Index on version
        [("timestamp", -1)],  # Descending index on timestamp for latest first
        [("project_id", 1), ("timestamp", -1)]  # Compound index for project logs by date
    ]
}

# Default values for documents
# Type hint for DEFAULT_VALUES
DefaultValues = Dict[str, Dict[str, Any]]

DEFAULT_VALUES: DefaultValues = {
    "users": {
        "preferences": {},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    "projects": {
        "current_version": 0,
        "ai_model_used": None,
        "status": ProjectStatus.DRAFT.value,
        "latest_s3_input": None,
        "latest_s3_output": [],
        "metadata": {},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    "messages": {
        "metadata": {},
        "timestamp": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    "files": {
        "metadata": {},
        "timestamp": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    "logs": {
        "metadata": {},
        "timestamp": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
}

def get_current_time() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)