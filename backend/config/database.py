"""Database connection configuration."""
from typing import Dict, Any, List, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_CONFIG: Dict[str, Any] = {
    'uri': os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
    'database': os.getenv('MONGODB_DATABASE', 'cadscribe'),
    'options': {
        'serverSelectionTimeoutMS': 5000,
        'connectTimeoutMS': 10000,
        'socketTimeoutMS': 45000,
        'maxPoolSize': 50,
        'minPoolSize': 10,
        'maxIdleTimeMS': 60000,
        'waitQueueTimeoutMS': 5000,
        'retryWrites': True,
        'w': 'majority',
        'journal': True,
    }
}

# Collection Names
class Collections:
    USERS = "users"
    PROJECTS = "projects"
    MODELS = "models"
    CHAT_MESSAGES = "chat_messages"

# Index Configuration
INDEXES: Dict[str, List[List[Tuple[str, int]]]] = {
    Collections.USERS: [
        [("email", 1)],
        [("created_at", 1)]
    ],
    Collections.PROJECTS: [
        [("user_id", 1)],
        [("created_at", -1)]
    ],
    Collections.MODELS: [
        [("user_id", 1)],
        [("project_id", 1)],
        [("created_at", -1)]
    ],
    Collections.CHAT_MESSAGES: [
        [("project_id", 1)],
        [("created_at", 1)]
    ]
}

# Default field values
DEFAULT_VALUES: Dict[str, Dict[str, Any]] = {
    Collections.USERS: {
        "preferences": {},
        "is_active": True
    },
    Collections.PROJECTS: {
        "models": [],
        "chat_history": [],
        "is_archived": False
    },
    Collections.MODELS: {
        "version": "1.0.0",
        "preview_url": None
    },
    Collections.CHAT_MESSAGES: {
        "related_model_id": None
    }
}