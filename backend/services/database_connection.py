"""Database connection manager."""
import contextlib
import functools
from typing import Any, Dict, Optional, List, Callable, TypeVar, Generator, Union
from datetime import datetime
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import (
    ConnectionFailure, ServerSelectionTimeoutError,
    DuplicateKeyError, OperationFailure
)
from bson import ObjectId

from .config.database import MONGODB_CONFIG, Collections, INDEXES

logger = logging.getLogger(__name__)

T = TypeVar('T')

def handle_db_error(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle database errors."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except ConnectionFailure as e:
            logger.error(f"Database connection error in {func.__name__}: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            logger.error(f"Database server selection timeout in {func.__name__}: {e}")
            raise
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error in {func.__name__}: {e}")
            raise
        except OperationFailure as e:
            logger.error(f"Operation failure in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    return wrapper

class DatabaseConnection:
    """MongoDB connection manager with context support."""
    
    def __init__(self) -> None:
        """Initialize the database connection."""
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        
    def __enter__(self) -> 'DatabaseConnection':
        self.connect()
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.disconnect()
        
    def connect(self) -> None:
        """Connect to MongoDB with retry logic."""
        if not self.client:
            try:
                self.client = MongoClient(
                    MONGODB_CONFIG['uri'],
                    **MONGODB_CONFIG['options']
                )
                self.db = self.client[MONGODB_CONFIG['database']]
                self.client.admin.command('ping')
                self._ensure_indexes()
                logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                self.disconnect()
                raise
                
    def disconnect(self) -> None:
        """Safely disconnect from MongoDB."""
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self.client = None
            self.db = None
            
    def _ensure_indexes(self) -> None:
        """Create necessary indexes if they don't exist."""
        if not self.db:
            return
            
        for collection_name, indexes in INDEXES.items():
            collection = self.db[collection_name]
            existing = {idx['name'] for idx in collection.list_indexes()}
            
            for index in indexes:
                name = f"{index[0][0]}_{index[0][1]}"
                if name not in existing:
                    try:
                        collection.create_index(index[0], background=True)
                        logger.info(f"Created index {name} on {collection_name}")
                    except Exception as e:
                        logger.error(f"Failed to create index {name}: {e}")
                        
    @contextlib.contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Context manager for database transactions."""
        if not self.client:
            raise ConnectionFailure("Not connected to database")
            
        with self.client.start_session() as session:
            with session.start_transaction():
                try:
                    yield
                except Exception as e:
                    session.abort_transaction()
                    logger.error(f"Transaction aborted: {e}")
                    raise
                    
    def get_collection(self, name: str) -> Collection:
        """Get a collection with proper error handling."""
        if not self.db:
            raise ConnectionFailure("Not connected to database")
        return self.db[name]
        
    @handle_db_error
    def insert_document(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a document with proper error handling."""
        if not self.db:
            raise ConnectionFailure("Not connected to database")
            
        # Add timestamps
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = document['created_at']
        
        # Add default values
        if collection in INDEXES:
            document.update(INDEXES[collection])
            
        result = self.db[collection].insert_one(document)
        return str(result.inserted_id)
        
    @handle_db_error
    def find_document(
        self, 
        collection: str,
        query: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Find a single document with proper error handling."""
        if not self.db:
            raise ConnectionFailure("Not connected to database")
            
        result = self.db[collection].find_one(query, projection)
        if result:
            result['id'] = str(result['_id'])
            del result['_id']
        return result
        
    @handle_db_error
    def update_document(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any]
    ) -> bool:
        """Update a document with proper error handling."""
        if not self.db:
            raise ConnectionFailure("Not connected to database")
            
        # Add updated timestamp
        update['$set'] = update.get('$set', {})
        update['$set']['updated_at'] = datetime.utcnow()
        
        result = self.db[collection].update_one(query, update)
        return result.modified_count > 0
        
    @handle_db_error
    def delete_document(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a document with proper error handling."""
        if not self.db:
            raise ConnectionFailure("Not connected to database")
            
        result = self.db[collection].delete_one(query)
        return result.deleted_count > 0
        
    @handle_db_error
    def find_documents(
        self,
        collection: str,
        query: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple[str, int]]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find multiple documents with proper error handling."""
        if not self.db:
            raise ConnectionFailure("Not connected to database")
            
        cursor = self.db[collection].find(query, projection)
        
        if sort:
            cursor = cursor.sort(sort)
            
        cursor = cursor.skip(skip).limit(limit)
        
        results = []
        for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            results.append(doc)
            
        return results