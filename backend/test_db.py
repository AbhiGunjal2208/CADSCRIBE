#!/usr/bin/env python3
"""
Simple database connection test script.
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from services.database import db_service
    from config import settings
    
    print("🔍 Testing Database Connection...")
    print(f"📡 MongoDB URI: {settings.mongodb_uri}")
    print(f"🗄️  Database Name: {settings.database_name}")
    
    # Test connection
    if db_service.client:
        print("✅ Database client created successfully")
        
        # Test ping
        try:
            db_service.client.admin.command('ping')
            print("✅ Database ping successful - Connection is working!")
            
            # Test database access
            db = db_service.client[settings.database_name]
            collections = db.list_collection_names()
            print(f"📋 Available collections: {collections}")
            
            # Test creating a test document
            test_doc = {
                "test": True,
                "message": "Database connection test",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            result = db.test_collection.insert_one(test_doc)
            print(f"✅ Test document inserted with ID: {result.inserted_id}")
            
            # Clean up test document
            db.test_collection.delete_one({"_id": result.inserted_id})
            print("🧹 Test document cleaned up")
            
            print("\n🎉 Database connection test PASSED!")
            
        except Exception as e:
            print(f"❌ Database ping failed: {e}")
            sys.exit(1)
    else:
        print("❌ Database client creation failed")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

