"""
Project-centric database service for the new MongoDB schema.
Handles all CRUD operations for projects, messages, files, and logs.
"""
import logging
import uuid
from typing import Optional, Dict, Any, List
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import (
    ConnectionFailure, DuplicateKeyError, 
    OperationFailure, ServerSelectionTimeoutError
)
from datetime import datetime, timezone
from bson import ObjectId

from models.schema import (
    Project, Message, File, Log, 
    ProjectStatus, MessageRole, FileType,
    INDEXES, DEFAULT_VALUES, get_current_time
)
from config import settings

logger = logging.getLogger(__name__)


class Collections:
    """Collection names for the new schema."""
    USERS = "users"
    PROJECTS = "projects"
    MESSAGES = "messages"
    FILES = "files"
    LOGS = "logs"
    # Legacy collection for migration
    CHAT_MESSAGES = "chat_messages"


class ProjectService:
    """Project-centric database service with the new schema."""
    
    def __init__(self):
        """Initialize the project service with database connection."""
        self.client: Optional[MongoClient[Dict[str, Any]]] = None
        self.db: Optional[Database[Dict[str, Any]]] = None
        logger.info(" Initializing ProjectService...")
        self._connect()
        if self.db is not None:
            logger.info("ProjectService initialized with database connection")
        else:
            logger.warning("ProjectService initialized without database connection (demo mode)")
    
    def _connect(self) -> None:
        """Connect to MongoDB with proper configuration."""
        try:
            # Connection with proper configuration
            self.client = MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=2000,
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
    
    # Project operations
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """Create a new project with auto-generated project_id."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Generate unique project_id
            project_id = f"project-{str(uuid.uuid4())[:8]}"
            
            # Apply default values
            project_doc = DEFAULT_VALUES["projects"].copy()
            project_doc.update(project_data)
            project_doc["project_id"] = project_id
            
            result = self.db[Collections.PROJECTS].insert_one(project_doc)
            logger.info(f"Created project {project_id} with MongoDB ID {result.inserted_id}")
            return project_id
            
        except DuplicateKeyError:
            # Retry with new project_id
            return self.create_project(project_data)
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by project_id."""
        try:
            # Check and reconnect if needed
            self._reconnect_if_needed()
            
            if self.db is None:
                logger.error(f"Database not connected, cannot get project {project_id}")
                return None
                
            # Try multiple ways to find the project
            logger.info(f"🔍 Looking for project with ID: {project_id}")
            
            # Method 1: Try by "id" field (string)
            project = self.db[Collections.PROJECTS].find_one({"id": project_id})
            if project:
                logger.info("✅ Found project by 'id' field")
            else:
                # Method 2: Try by "project_id" field
                project = self.db[Collections.PROJECTS].find_one({"project_id": project_id})
                if project:
                    logger.info("✅ Found project by 'project_id' field")
                else:
                    # Method 3: Try by ObjectId if it looks like one
                    try:
                        from bson import ObjectId
                        if len(project_id) == 24:  # ObjectId length
                            project = self.db[Collections.PROJECTS].find_one({"_id": ObjectId(project_id)})
                            if project:
                                logger.info("✅ Found project by ObjectId")
                    except Exception as oid_error:
                        logger.warning(f"ObjectId lookup failed: {oid_error}")
                
                if not project:
                    logger.warning(f"❌ Project {project_id} not found by any method")
            if project:
                project["id"] = str(project["_id"])
                del project["_id"]
            return project
        except Exception as e:
            logger.error(f"Failed to get project by ID {project_id}: {e}")
            return None
    
    def get_user_projects(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all projects for a user."""
        try:
            if self.db is None:
                logger.warning("Database not connected, returning empty projects list")
                return []
                
            cursor = self.db[Collections.PROJECTS].find(
                {"user_id": user_id}  # Fixed: should be user_id, not created_by
            ).sort("updated_at", DESCENDING).skip(skip).limit(limit)
            
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
            # Check and reconnect if needed
            self._reconnect_if_needed()
            
            if self.db is None:
                logger.error(f"Database not connected, cannot update project {project_id}")
                return False
            
            # Add updated_at timestamp
            update_data["updated_at"] = get_current_time()
            
            logger.info(f"Updating project {project_id} with data: {update_data}")
            result = self.db[Collections.PROJECTS].update_one(
                {"project_id": project_id},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            logger.info(f"Project {project_id} update result: modified_count={result.modified_count}, matched_count={result.matched_count}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all associated data."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # First, find the project to get its actual database ID
            project = self.get_project_by_id(project_id)
            if not project:
                logger.warning(f"Project {project_id} not found for deletion")
                return False
            
            # Use multiple field strategies for deletion
            delete_queries = [
                {"id": project_id},
                {"project_id": project_id}
            ]
            
            # Try ObjectId if it looks like one
            try:
                from bson import ObjectId
                if len(project_id) == 24:
                    delete_queries.append({"_id": ObjectId(project_id)})
            except:
                pass
            
            # Delete associated messages
            for query in delete_queries:
                self.db[Collections.MESSAGES].delete_many(query)
            
            # Delete associated files  
            for query in delete_queries:
                self.db[Collections.FILES].delete_many(query)
            
            # Delete associated logs
            for query in delete_queries:
                self.db[Collections.LOGS].delete_many(query)
            
            # Delete the project - try all query methods
            deleted_count = 0
            for query in delete_queries:
                result = self.db[Collections.PROJECTS].delete_one(query)
                deleted_count += result.deleted_count
                if result.deleted_count > 0:
                    logger.info(f"✅ Project deleted using query: {query}")
                    break
            
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            return False
    
    # Message operations
    def create_message(self, message_data: Dict[str, Any]) -> str:
        """Create a new message."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Apply default values
            message_doc = DEFAULT_VALUES["messages"].copy()
            message_doc.update(message_data)
            
            result = self.db[Collections.MESSAGES].insert_one(message_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            raise
    
    def get_project_messages(self, project_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a project."""
        try:
            if self.db is None:
                logger.warning(f"Database not connected, returning empty messages for project {project_id}")
                return []
                
            logger.info(f"Fetching messages for project {project_id}")
            
            # Try multiple field strategies for finding messages
            message_queries = [
                {"project_id": project_id},
                {"id": project_id}
            ]
            
            # Try ObjectId if it looks like one
            try:
                from bson import ObjectId
                if len(project_id) == 24:
                    message_queries.append({"project_id": ObjectId(project_id)})
                    message_queries.append({"id": ObjectId(project_id)})
            except:
                pass
            
            messages = []
            for query in message_queries:
                try:
                    cursor = self.db[Collections.MESSAGES].find(query).sort("timestamp", ASCENDING).skip(skip).limit(limit)
                    
                    for message in cursor:
                        message["id"] = str(message["_id"])
                        del message["_id"]
                        messages.append(message)
                    
                    if messages:
                        logger.info(f"✅ Found {len(messages)} messages using query: {query}")
                        break
                    else:
                        logger.info(f"⚠️ No messages found with query: {query}")
                except Exception as query_error:
                    logger.warning(f"Query failed {query}: {query_error}")
                    continue
            
            logger.info(f"Total messages found for project {project_id}: {len(messages)}")
            return messages
        except Exception as e:
            logger.error(f"Failed to get project messages for {project_id}: {e}")
            return []
    
    # File operations
    def create_file_record(self, file_data: Dict[str, Any]) -> str:
        """Create a new file record."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Apply default values
            file_doc = DEFAULT_VALUES["files"].copy()
            file_doc.update(file_data)
            
            result = self.db[Collections.FILES].insert_one(file_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create file record: {e}")
            raise
    
    def get_project_files(self, project_id: str, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get files for a project, optionally filtered by type."""
        try:
            if self.db is None:
                return []
            
            query = {"project_id": project_id}
            if file_type:
                query["file_type"] = file_type
                
            cursor = self.db[Collections.FILES].find(query).sort("version", DESCENDING)
            
            files = []
            for file in cursor:
                file["id"] = str(file["_id"])
                del file["_id"]
                files.append(file)
                
            return files
        except Exception as e:
            logger.error(f"Failed to get project files: {e}")
            return []
    
    def get_latest_file_by_type(self, project_id: str, file_type: str) -> Optional[Dict[str, Any]]:
        """Get the latest file of a specific type for a project."""
        try:
            if self.db is None:
                return None
                
            file = self.db[Collections.FILES].find_one(
                {"project_id": project_id, "file_type": file_type},
                sort=[("version", DESCENDING)]
            )
            
            if file:
                file["id"] = str(file["_id"])
                del file["_id"]
            return file
        except Exception as e:
            logger.error(f"Failed to get latest file: {e}")
            return None
    
    # Log operations
    def create_log_record(self, log_data: Dict[str, Any]) -> str:
        """Create a new log record."""
        try:
            if self.db is None:
                raise ConnectionFailure("Database not connected")
            
            # Apply default values
            log_doc = DEFAULT_VALUES["logs"].copy()
            log_doc.update(log_data)
            
            result = self.db[Collections.LOGS].insert_one(log_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create log record: {e}")
            raise
    
    def get_project_logs(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get logs for a project."""
        try:
            if self.db is None:
                return []
                
            cursor = self.db[Collections.LOGS].find(
                {"project_id": project_id}
            ).sort("timestamp", DESCENDING).limit(limit)
            
            logs = []
            for log in cursor:
                log["id"] = str(log["_id"])
                del log["_id"]
                logs.append(log)
                
            return logs
        except Exception as e:
            logger.error(f"Failed to get project logs: {e}")
            return []
    
    # Comprehensive project data operations
    def get_project_with_data(self, project_id: str, include_messages: bool = True, 
                             include_files: bool = True, include_logs: bool = True) -> Optional[Dict[str, Any]]:
        """Get project with all associated data."""
        try:
            project = self.get_project_by_id(project_id)
            if not project:
                return None
            
            # Add associated data
            if include_messages:
                project["messages"] = self.get_project_messages(project_id)
            
            if include_files:
                project["files"] = self.get_project_files(project_id)
                # Group files by type for easier access
                project["files_by_type"] = {}
                for file in project["files"]:
                    file_type = file["file_type"]
                    if file_type not in project["files_by_type"]:
                        project["files_by_type"][file_type] = []
                    project["files_by_type"][file_type].append(file)
            
            if include_logs:
                project["logs"] = self.get_project_logs(project_id)
            
            return project
            
        except Exception as e:
            logger.error(f"Failed to get project with data: {e}")
            return None
    
    def update_project_version(self, project_id: str, version: int, 
                              ai_model: str = None, s3_input_path: str = None) -> bool:
        """Update project version and related metadata."""
        try:
            update_data = {
                "current_version": version,
                "status": ProjectStatus.PROCESSING.value,
                "updated_at": get_current_time()
            }
            
            if ai_model:
                update_data["ai_model_used"] = ai_model
            
            if s3_input_path:
                update_data["latest_s3_input"] = s3_input_path
            
            return self.update_project(project_id, update_data)
            
        except Exception as e:
            logger.error(f"Failed to update project version: {e}")
            return False
    
    def mark_project_completed(self, project_id: str, output_files: List[str]) -> bool:
        """Mark project as completed with output files."""
        try:
            update_data = {
                "status": ProjectStatus.COMPLETED.value,
                "latest_s3_output": output_files,
                "updated_at": get_current_time()
            }
            
            return self.update_project(project_id, update_data)
            
        except Exception as e:
            logger.error(f"Failed to mark project completed: {e}")
            return False
    
    def _check_connection(self) -> bool:
        """Check if database connection is healthy."""
        try:
            if self.client is None or self.db is None:
                return False
            
            # Test connection with ping
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def _reconnect_if_needed(self) -> None:
        """Reconnect to database if connection is lost."""
        if not self._check_connection():
            logger.warning("Database connection lost, attempting to reconnect...")
            self._connect()
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()


# Global project service instance
project_service = ProjectService()
