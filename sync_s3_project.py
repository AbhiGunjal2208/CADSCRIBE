#!/usr/bin/env python3
"""
Script to sync S3 project files with database entries
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.project_service import project_service
from datetime import datetime

def create_project_for_s3_files():
    """Create database entry for S3 project files"""
    try:
        # Project data for the S3 files we found
        project_data = {
            "title": "S3 Project 3518c842",
            "description": "Project synced from S3 files",
            "user_id": "demo-user",
            "metadata": {
                "engine": "freecad",
                "parameters": {}
            },
            "current_version": 1,
            "ai_model_used": "freecad",
            "status": "completed",
            "latest_s3_input": {"project_name": "project-3518c842"},
            "latest_s3_output": [
                {"format": "STL", "filename": "project-3518c842.stl", "version": 1},
                {"format": "STEP", "filename": "project-3518c842.step", "version": 1},
                {"format": "IGES", "filename": "project-3518c842.iges", "version": 1},
                {"format": "OBJ", "filename": "project-3518c842-842.obj", "version": 1},
                {"format": "FCSTD", "filename": "project-3518c842.fcstd", "version": 1}
            ]
        }
        
        # Create the project
        project_id = project_service.create_project(project_data)
        print(f"✅ Created project with ID: {project_id}")
        
        # Verify it was created
        created_project = project_service.get_project_by_id(project_id)
        if created_project:
            print(f"✅ Project verified: {created_project.get('title')}")
            print(f"📁 S3 project name: {created_project.get('latest_s3_input', {}).get('project_name')}")
            print(f"📄 Output files: {len(created_project.get('latest_s3_output', []))}")
        else:
            print("❌ Failed to verify created project")
            
    except Exception as e:
        print(f"❌ Error creating project: {e}")

if __name__ == "__main__":
    print("🔄 Syncing S3 project with database...")
    create_project_for_s3_files()
    print("✅ Sync complete!")
