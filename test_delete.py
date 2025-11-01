import requests
import json

try:
    # Test DELETE endpoint
    url = "http://localhost:8000/api/projects/68ea0cd1a841f832d3f11c55"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJleHAiOjE3OTIzMzgzMDgsImlhdCI6MTc2MDgwMjMwOH0.XFJFsShSYLFVe6AYjmDBEPbkB1lyxoyaHfgWi7yfwvI"
    }
    
    print("Testing DELETE endpoint...")
    response = requests.delete(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
except Exception as e:
    print(f"Error making request: {e}")
