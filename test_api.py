import requests
import json

try:
    url = "http://localhost:8000/api/projects/68f3c9a08baa5e3ffe6c8a1d/chat"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vLXVzZXIiLCJleHAiOjE3OTIzMzgzMDgsImlhdCI6MTc2MDgwMjMwOH0.XFJFsShSYLFVe6AYjmDBEPbkB1lyxoyaHfgWi7yfwvI"
    }
    
    print("Testing API endpoint...")
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 500:
        print("Server returned 500 error - checking if it's a JSON response...")
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
        except:
            print("Response is not JSON")
            
except Exception as e:
    print(f"Error making request: {e}")
