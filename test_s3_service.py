#!/usr/bin/env python3
"""
Test S3 service directly
"""
import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.s3_service import s3_service

async def test_s3_service():
    """Test S3 service check_output_files method"""
    try:
        print("🔄 Testing S3 service check_output_files...")
        
        # Test with the project name we know has files
        project_name = "project-3518c842"
        
        print(f"🔍 Checking files for project: {project_name}")
        files = await s3_service.check_output_files(project_name)
        
        print(f"✅ Found {len(files)} files:")
        for file in files:
            print(f"   📄 {file.get('filename')} - Format: {file.get('format')} - Version: {file.get('version')} - Size: {file.get('size')}")
        
        # Test specific format lookup
        stl_files = [f for f in files if f.get('format', '').upper() == 'STL']
        print(f"\n🔍 STL files found: {len(stl_files)}")
        for file in stl_files:
            print(f"   📄 {file.get('filename')} - {file.get('format')}")
            
    except Exception as e:
        print(f"❌ Error testing S3 service: {e}")

if __name__ == "__main__":
    print("🔄 Testing S3 service...")
    asyncio.run(test_s3_service())
    print("✅ Test complete!")
