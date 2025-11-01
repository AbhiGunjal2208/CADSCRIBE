"""
Database service for MongoDB operations.
"""
from typing import Optional, Dict, Any, List, TypeVar, Generic, Union
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.errors import (
    ConnectionFailure, DuplicateKeyError, 
    OperationFailure, ServerSelectionTimeoutError
)
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from datetime import datetime, timezone
import logging
from bson import ObjectId
from models.schema import (
    User, Project, Message, LegacyChatMessage, 
    INDEXES, DEFAULT_VALUES, get_current_time
)
from config import settings

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Collections:
    """Collection names for MongoDB."""
    USERS = "users"
    MODELS = "models"
    CHAT_MESSAGES = "chat_messages"
    PROJECTS = "projects"

class DatabaseService:
    """MongoDB database service with typed collections."""
    
    def __init__(self):
        """Initialize database service with None values."""
        self.client: Optional[MongoClient[Dict[str, Any]]] = None
        self.db: Optional[Database[Dict[str, Any]]] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to MongoDB with proper configuration."""
        try:
            # Connection with proper configuration
            self.client = MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=2000,  # Reduced to 2 seconds for faster failure
                connectTimeoutMS=2000,
                socketTimeoutMS=2000,
                maxPoolSize=10,
                retryWrites=True
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[settings.database_name]
            logger.info("Successfully connected to MongoDB")
            
        except ServerSelectionTimeoutError:
            logger.warning("MongoDB server selection timeout - running in demo mode without database")
            self.client = None
            self.db = None
        except ConnectionFailure as e:
            logger.warning(f"Failed to connect to MongoDB: {e} - running in demo mode without database")
            self.client = None
            self.db = None
        except Exception as e:
            logger.error(f"Unexpected database connection error: {e}")
            self.client = None
            self.db = None
    
    def _create_indexes(self) -> None:
        """Create database indexes for better performance."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            # Create indexes for all collections based on schema configuration
            for collection_name, index_list in INDEXES.items():
                collection: Collection[Dict[str, Any]] = self.db[collection_name]
                
                # Get existing indexes
                existing_indexes = set(idx['name'] for idx in collection.list_indexes())
                
                # Create missing indexes
                for index_keys in index_list:
                    try:
                        # Generate index name for comparison
                        index_name = "_".join([f"{field}_{direction}" for field, direction in index_keys])
                        if not any(idx['name'] == index_name for idx in collection.list_indexes()):
                            collection.create_index(index_keys)
                    except OperationFailure as e:
                        logger.error(f"Failed to create index {index_keys}: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Apply default values
            user_data.update(DEFAULT_VALUES["users"])
            
            result = self.db[Collections.USERS].insert_one(user_data)
            return str(result.inserted_id)
            
        except DuplicateKeyError:
            raise ValueError("User with this email already exists")
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            user = self.db[Collections.USERS].find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            user = self.db[Collections.USERS].find_one({"email": email})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user profile and preferences."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Add updated_at timestamp
            update_data["updated_at"] = get_current_time()
            
            result = self.db[Collections.USERS].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all associated data."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Delete all user's projects (this will cascade delete models and chat messages)
            projects = self.get_user_projects(user_id)
            for project in projects:
                self.delete_project(project["id"])
            
            # Delete any remaining models not associated with projects
            self.db[Collections.MODELS].delete_many({"user_id": user_id})
            
            # Delete any remaining chat messages
            self.db[Collections.CHAT_MESSAGES].delete_many({"user_id": user_id})
            
            # Delete the user
            result = self.db[Collections.USERS].delete_one({"_id": ObjectId(user_id)})
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False

    # Project operations
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """Create a new project."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Apply default values
            project_data.update(DEFAULT_VALUES["projects"])
            
            result = self.db[Collections.PROJECTS].insert_one(project_data)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            project = self.db[Collections.PROJECTS].find_one({"_id": ObjectId(project_id)})
            if project:
                project["id"] = str(project["_id"])
                del project["_id"]
            return project
        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            return None

    def get_user_projects(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all projects for a user."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            cursor = self.db[Collections.PROJECTS].find(
                {"user_id": user_id}
            ).sort("created_at", DESCENDING).skip(skip).limit(limit)
            
            projects = []
            for project in cursor:
                project["id"] = str(project["_id"])
                del project["_id"]
                projects.append(project)
            
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get user projects: {e}")
            return []
    
    def update_project(self, project_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a project."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Add updated_at timestamp
            update_data["updated_at"] = get_current_time()
            
            result = self.db[Collections.PROJECTS].update_one(
                {"_id": ObjectId(project_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update project: {e}")
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all associated data."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Delete associated chat messages
            self.db[Collections.CHAT_MESSAGES].delete_many({"project_id": project_id})
            
            # Delete associated models
            self.db[Collections.MODELS].delete_many({"project_id": project_id})
            
            # Delete the project
            result = self.db[Collections.PROJECTS].delete_one({"_id": ObjectId(project_id)})
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            return False

    # Model operations
    def create_model(self, model_data: Dict[str, Any]) -> str:
        """Create a new CAD model."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Apply default values
            model_data.update(DEFAULT_VALUES["models"])
            
            result = self.db[Collections.MODELS].insert_one(model_data)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            raise

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model by ID."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            model = self.db[Collections.MODELS].find_one({"_id": ObjectId(model_id)})
            if model:
                model["id"] = str(model["_id"])
                del model["_id"]
            return model
        except Exception as e:
            logger.error(f"Failed to get model: {e}")
            return None

    def get_user_models(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all models for a user."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            cursor = self.db[Collections.MODELS].find(
                {"user_id": user_id}
            ).sort("created_at", DESCENDING).skip(skip).limit(limit)
            
            models = []
            for model in cursor:
                model["id"] = str(model["_id"])
                del model["_id"]
                models.append(model)
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to get user models: {e}")
            return []

    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> bool:
        """Update a project."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            # Add updated timestamp
            project_data["updated_at"] = datetime.utcnow()
            
            result = self.db[Collections.PROJECTS].update_one(
                {"_id": ObjectId(project_id)},
                {"$set": project_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update project: {e}")
            raise

    def delete_project(self, project_id: str) -> bool:
        """Delete a project and its associated data."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
                
            # Delete project
            project_result = self.db[Collections.PROJECTS].delete_one({"_id": ObjectId(project_id)})
            
            # Delete associated chat history
            self.db[Collections.CHAT_MESSAGES].delete_many({"project_id": project_id})
            
            return project_result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            raise

    # Chat operations
    def create_chat_message(self, message_data: Dict[str, Any]) -> str:
        """Create a new chat message."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Apply default values
            message_data.update(DEFAULT_VALUES["chat_messages"])
            
            result = self.db[Collections.CHAT_MESSAGES].insert_one(message_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create chat message: {e}")
            raise

    def get_chat_history(self, project_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a project."""
        try:
            if self.db is None:
                return []
                
            messages = list(self.db[Collections.CHAT_MESSAGES].find(
                {"project_id": project_id}
            ).sort("timestamp", 1))
            
            # Convert ObjectId to string
            for message in messages:
                message["id"] = str(message["_id"])
                del message["_id"]
                
            return messages
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return []

    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()


# Global database service instance
db_service = DatabaseService()
