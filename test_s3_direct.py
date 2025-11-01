#!/usr/bin/env python3
"""
Direct S3 test to see what files exist
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.s3_service import s3_service

def test_s3_direct():
    """Test S3 directly to see what files exist"""
    try:
        if not s3_service.s3_client:
            print("❌ S3 client not initialized")
            return
            
        print(f"🔍 Testing S3 bucket: {s3_service.aws_bucket_name}")
        
        # Test different path structures
        test_paths = [
            "output/project-3518c842/",
            "output/project-3518c842/v1/",
            "project-3518c842/",
            "project-3518c842/v1/"
        ]
        
        for path in test_paths:
            print(f"\n🔍 Checking path: {path}")
            try:
                response = s3_service.s3_client.list_objects_v2(
                    Bucket=s3_service.aws_bucket_name,
                    Prefix=path
                )
                
                if 'Contents' in response:
                    print(f"✅ Found {len(response['Contents'])} files:")
                    for obj in response['Contents']:
                        print(f"   📄 {obj['Key']} ({obj['Size']} bytes)")
                else:
                    print("❌ No files found")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Also check the root output folder
        print(f"\n🔍 Checking root output folder:")
        try:
            response = s3_service.s3_client.list_objects_v2(
                Bucket=s3_service.aws_bucket_name,
                Prefix="output/",
                Delimiter="/"
            )
            
            if 'CommonPrefixes' in response:
                print(f"✅ Found project folders:")
                for prefix in response['CommonPrefixes']:
                    print(f"   📁 {prefix['Prefix']}")
            else:
                print("❌ No project folders found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
    except Exception as e:
        print(f"❌ Error testing S3: {e}")

if __name__ == "__main__":
    print("🔄 Testing S3 direct access...")
    test_s3_direct()
    print("✅ Test complete!")
