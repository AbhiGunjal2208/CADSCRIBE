"""
Data migration script to convert from flat message structure to project-centric schema.
Migrates existing chat_messages to the new projects/messages/files/logs structure.
"""
import logging
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import db_service
from services.project_service import project_service, Collections
from models.schema import ProjectStatus, MessageRole, FileType, get_current_time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SchemaMigration:
    """Handles migration from old schema to new project-centric schema."""
    
    def __init__(self):
        self.migration_stats = {
            "legacy_messages_found": 0,
            "projects_created": 0,
            "messages_migrated": 0,
            "files_created": 0,
            "errors": 0
        }
    
    def run_migration(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Run the complete migration process.
        
        Args:
            dry_run: If True, only analyze data without making changes
            
        Returns:
            Migration statistics and results
        """
        logger.info(f"Starting schema migration (dry_run={dry_run})")
        
        try:
            # Step 1: Analyze existing data
            legacy_messages = self._get_legacy_messages()
            self.migration_stats["legacy_messages_found"] = len(legacy_messages)
            
            if not legacy_messages:
                logger.info("No legacy messages found. Migration not needed.")
                return self.migration_stats
            
            # Step 2: Group messages by project
            project_groups = self._group_messages_by_project(legacy_messages)
            
            # Step 3: Create projects and migrate data
            if not dry_run:
                self._migrate_project_groups(project_groups)
            else:
                logger.info(f"DRY RUN: Would create {len(project_groups)} projects")
                for project_key, messages in project_groups.items():
                    logger.info(f"  Project '{project_key}': {len(messages)} messages")
            
            logger.info("Migration completed successfully")
            return self.migration_stats
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.migration_stats["errors"] += 1
            raise
    
    def _get_legacy_messages(self) -> List[Dict[str, Any]]:
        """Get all messages from the legacy chat_messages collection."""
        try:
            if not db_service.db:
                raise Exception("Database not connected")
            
            # Get all messages from legacy collection
            messages = list(db_service.db[Collections.CHAT_MESSAGES].find({}))
            
            # Convert ObjectId to string
            for message in messages:
                message["id"] = str(message["_id"])
                del message["_id"]
            
            logger.info(f"Found {len(messages)} legacy messages")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get legacy messages: {e}")
            return []
    
    def _group_messages_by_project(self, messages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group messages by project_id, creating default projects for orphaned messages."""
        project_groups = {}
        
        for message in messages:
            # Get project_id from message, or create a default one
            project_id = message.get("project_id")
            
            if not project_id or project_id == "default":
                # Create project_id based on user_id for orphaned messages
                user_id = message.get("user_id", "unknown")
                project_id = f"migrated-{user_id}-{str(uuid.uuid4())[:8]}"
            
            if project_id not in project_groups:
                project_groups[project_id] = []
            
            project_groups[project_id].append(message)
        
        logger.info(f"Grouped messages into {len(project_groups)} projects")
        return project_groups
    
    def _migrate_project_groups(self, project_groups: Dict[str, List[Dict[str, Any]]]) -> None:
        """Migrate each project group to the new schema."""
        for project_id, messages in project_groups.items():
            try:
                self._migrate_single_project(project_id, messages)
                self.migration_stats["projects_created"] += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate project {project_id}: {e}")
                self.migration_stats["errors"] += 1
                continue
    
    def _migrate_single_project(self, project_id: str, messages: List[Dict[str, Any]]) -> None:
        """Migrate a single project and its messages."""
        logger.info(f"Migrating project {project_id} with {len(messages)} messages")
        
        # Determine project details from messages
        project_details = self._extract_project_details(project_id, messages)
        
        # Create project document
        project_data = {
            "project_id": project_id,
            "project_name": project_details["name"],
            "created_by": project_details["created_by"],
            "current_version": project_details["current_version"],
            "ai_model_used": project_details["ai_model_used"],
            "status": project_details["status"],
            "latest_s3_input": project_details["latest_s3_input"],
            "latest_s3_output": project_details["latest_s3_output"],
            "metadata": project_details["metadata"],
            "created_at": project_details["created_at"],
            "updated_at": project_details["updated_at"]
        }
        
        # Insert project (skip if already exists)
        existing_project = project_service.get_project_by_id(project_id)
        if not existing_project:
            # Create new project with specific project_id
            if project_service.db:
                project_service.db[Collections.PROJECTS].insert_one(project_data)
                logger.info(f"Created project: {project_id}")
        
        # Migrate messages
        for message in messages:
            self._migrate_message(project_id, message)
            self.migration_stats["messages_migrated"] += 1
        
        # Create file records from S3 references in messages
        self._create_file_records_from_messages(project_id, messages)
    
    def _extract_project_details(self, project_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract project details from messages."""
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda x: x.get("created_at", datetime.min))
        
        # Get first and last message for timestamps
        first_message = sorted_messages[0] if sorted_messages else {}
        last_message = sorted_messages[-1] if sorted_messages else {}
        
        # Extract details
        created_by = first_message.get("user_id", "unknown")
        created_at = first_message.get("created_at", get_current_time())
        updated_at = last_message.get("updated_at", get_current_time())
        
        # Determine project name
        if project_id.startswith("migrated-"):
            project_name = f"Migrated Project ({created_by})"
        elif project_id.startswith("demo-"):
            project_name = project_id.replace("-", " ").title()
        else:
            project_name = project_id.replace("_", " ").replace("-", " ").title()
        
        # Extract AI model and S3 info from messages
        ai_model_used = None
        latest_s3_input = None
        latest_s3_output = []
        current_version = 0
        
        for message in messages:
            metadata = message.get("metadata", {})
            
            # Extract AI model
            if metadata.get("source_model") and not ai_model_used:
                ai_model_used = metadata["source_model"]
            
            # Extract S3 URLs
            if metadata.get("s3_url"):
                latest_s3_input = metadata["s3_url"]
                if metadata.get("version"):
                    current_version = max(current_version, int(metadata["version"]))
        
        # Determine status
        status = ProjectStatus.DRAFT.value
        if latest_s3_input:
            status = ProjectStatus.PROCESSING.value
        if latest_s3_output:
            status = ProjectStatus.COMPLETED.value
        
        return {
            "name": project_name,
            "created_by": created_by,
            "current_version": current_version,
            "ai_model_used": ai_model_used,
            "status": status,
            "latest_s3_input": latest_s3_input,
            "latest_s3_output": latest_s3_output,
            "metadata": {
                "description": f"Migrated from legacy chat messages",
                "migration_date": get_current_time().isoformat()
            },
            "created_at": created_at,
            "updated_at": updated_at
        }
    
    def _migrate_message(self, project_id: str, legacy_message: Dict[str, Any]) -> None:
        """Migrate a single message to the new schema."""
        # Map legacy message to new schema
        message_data = {
            "project_id": project_id,
            "user_id": legacy_message.get("user_id", "unknown"),
            "role": legacy_message.get("role", MessageRole.USER.value),
            "content": legacy_message.get("content", ""),
            "timestamp": legacy_message.get("created_at", get_current_time()),
            "metadata": legacy_message.get("metadata", {}),
            "created_at": legacy_message.get("created_at", get_current_time()),
            "updated_at": legacy_message.get("updated_at", get_current_time())
        }
        
        # Insert message
        if project_service.db:
            project_service.db[Collections.MESSAGES].insert_one(message_data)
    
    def _create_file_records_from_messages(self, project_id: str, messages: List[Dict[str, Any]]) -> None:
        """Create file records based on S3 references in messages."""
        for message in messages:
            metadata = message.get("metadata", {})
            s3_url = metadata.get("s3_url")
            
            if s3_url:
                # Create file record
                file_data = {
                    "project_id": project_id,
                    "version": metadata.get("version", 1),
                    "file_type": FileType.INPUT.value,  # Assume input files from messages
                    "s3_path": s3_url,
                    "timestamp": message.get("created_at", get_current_time()),
                    "metadata": {
                        "file_name": s3_url.split("/")[-1] if "/" in s3_url else s3_url,
                        "ai_model": metadata.get("source_model"),
                        "uploaded_by": message.get("user_id"),
                        "generated_by": "cadscribe-ai",
                        "migrated_from_message": True
                    },
                    "created_at": message.get("created_at", get_current_time()),
                    "updated_at": message.get("updated_at", get_current_time())
                }
                
                if project_service.db:
                    project_service.db[Collections.FILES].insert_one(file_data)
                    self.migration_stats["files_created"] += 1
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify the migration results."""
        verification_results = {
            "projects_count": 0,
            "messages_count": 0,
            "files_count": 0,
            "logs_count": 0,
            "sample_projects": []
        }
        
        try:
            if not project_service.db:
                raise Exception("Database not connected")
            
            # Count documents in new collections
            verification_results["projects_count"] = project_service.db[Collections.PROJECTS].count_documents({})
            verification_results["messages_count"] = project_service.db[Collections.MESSAGES].count_documents({})
            verification_results["files_count"] = project_service.db[Collections.FILES].count_documents({})
            verification_results["logs_count"] = project_service.db[Collections.LOGS].count_documents({})
            
            # Get sample projects
            sample_projects = list(project_service.db[Collections.PROJECTS].find({}).limit(3))
            for project in sample_projects:
                project["id"] = str(project["_id"])
                del project["_id"]
                verification_results["sample_projects"].append(project)
            
            logger.info("Migration verification completed")
            return verification_results
            
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            return verification_results
    
    def rollback_migration(self) -> bool:
        """Rollback migration by dropping new collections (USE WITH CAUTION)."""
        try:
            if not project_service.db:
                raise Exception("Database not connected")
            
            logger.warning("ROLLING BACK MIGRATION - This will delete all new schema data!")
            
            # Drop new collections
            collections_to_drop = [Collections.PROJECTS, Collections.MESSAGES, Collections.FILES, Collections.LOGS]
            
            for collection_name in collections_to_drop:
                project_service.db[collection_name].drop()
                logger.info(f"Dropped collection: {collection_name}")
            
            logger.info("Migration rollback completed")
            return True
            
        except Exception as e:
            logger.error(f"Migration rollback failed: {e}")
            return False


def main():
    """Main migration script entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate to project-centric schema")
    parser.add_argument("--dry-run", action="store_true", help="Analyze data without making changes")
    parser.add_argument("--verify", action="store_true", help="Verify migration results")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration (DANGEROUS)")
    
    args = parser.parse_args()
    
    migration = SchemaMigration()
    
    if args.rollback:
        print("WARNING: This will delete all migrated data!")
        confirm = input("Type 'ROLLBACK' to confirm: ")
        if confirm == "ROLLBACK":
            migration.rollback_migration()
        else:
            print("Rollback cancelled")
        return
    
    if args.verify:
        results = migration.verify_migration()
        print("Migration Verification Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
        return
    
    # Run migration
    results = migration.run_migration(dry_run=args.dry_run)
    
    print("Migration Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    if args.dry_run:
        print("\nThis was a dry run. Use --no-dry-run to execute the migration.")
    else:
        print("\nMigration completed. Use --verify to check results.")


if __name__ == "__main__":
    main()
