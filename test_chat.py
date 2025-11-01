#!/usr/bin/env python3
"""
Test chat message storage and retrieval
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.project_service import project_service
from datetime import datetime

def test_chat_messages():
    """Test chat message functionality"""
    try:
        # Use the project we know exists
        project_id = "68f3c9a08baa5e3ffe6c8a1d"
        
        print(f"🔄 Testing chat messages for project: {project_id}")
        
        # First, verify project exists
        project = project_service.get_project_by_id(project_id)
        if not project:
            print(f"❌ Project {project_id} not found")
            return
        
        print(f"✅ Project found: {project.get('title')}")
        
        # Create a test message
        message_data = {
            "project_id": project_id,
            "role": "user",
            "content": "Test message from Python script",
            "timestamp": datetime.utcnow()
        }
        
        message_id = project_service.create_message(message_data)
        print(f"✅ Created test message with ID: {message_id}")
        
        # Retrieve messages
        messages = project_service.get_project_messages(project_id)
        print(f"✅ Retrieved {len(messages)} messages:")
        
        for msg in messages:
            print(f"   📄 {msg.get('role')}: {msg.get('content')[:50]}...")
        
        return len(messages) > 0
        
    except Exception as e:
        print(f"❌ Error testing chat messages: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Testing chat message functionality...")
    success = test_chat_messages()
    if success:
        print("✅ Chat messages working!")
    else:
        print("❌ Chat messages not working!")
