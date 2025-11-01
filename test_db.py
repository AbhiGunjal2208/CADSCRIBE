import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.project_service import project_service
from pymongo import MongoClient
from config.settings import settings

print("Testing database connection and project service...")

# Test direct MongoDB connection
try:
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client[settings.database_name]
    print("✅ Direct MongoDB connection successful")
    
    # Check collections
    collections = db.list_collection_names()
    print(f"📁 Available collections: {collections}")
    
    # Check projects collection
    if 'projects' in collections:
        project_count = db.projects.count_documents({})
        print(f"📊 Projects in database: {project_count}")
        
        # Get a sample project
        sample_project = db.projects.find_one()
        if sample_project:
            print(f"📄 Sample project keys: {list(sample_project.keys())}")
        else:
            print("📄 No projects found in database")
    else:
        print("⚠️ Projects collection does not exist")
        
except Exception as e:
    print(f"❌ Direct MongoDB connection failed: {e}")

# Test project service
try:
    print("\n🔧 Testing project service...")
    print(f"Project service DB connected: {project_service.db is not None}")
    
    if project_service.db is not None:
        # Test get_user_projects for demo user
        demo_projects = project_service.get_user_projects("demo-user")
        print(f"📋 Demo user projects: {len(demo_projects)} found")
        
        if demo_projects:
            print(f"📄 First project keys: {list(demo_projects[0].keys())}")
            print(f"📄 First project: {demo_projects[0]}")
        
        # Check what users exist in the database
        if project_service.db is not None:
            users = list(project_service.db.users.find({}, {"_id": 1, "email": 1, "name": 1}).limit(5))
            print(f"📋 Users in database: {len(users)} found")
            for user in users:
                user_id = str(user["_id"])
                user_projects = project_service.get_user_projects(user_id)
                print(f"📄 User {user.get('email', user_id)}: {len(user_projects)} projects")
                if user_projects:
                    print(f"   First project ID: {user_projects[0].get('id')}")
        
        # Test get_user_projects for a regular user
        regular_projects = project_service.get_user_projects("test-user")
        print(f"📋 Test user projects: {len(regular_projects)} found")
        
    else:
        print("❌ Project service database not connected")
        
except Exception as e:
    print(f"❌ Project service test failed: {e}")
    import traceback
    traceback.print_exc()
