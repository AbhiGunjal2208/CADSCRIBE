import jwt
from datetime import datetime, timezone, timedelta

# Same secret key as in backend settings
SECRET_KEY = "TJTLwsfWFEwxPqkhCYj1IdfnG5LJ2baCiXylq9hYt6joGdA6W9IjBze-G4Vnk9kuvWk"
ALGORITHM = "HS256"

# Create a demo user token that expires in 1 year
payload = {
    "sub": "demo-user",  # user ID
    "exp": datetime.now(timezone.utc) + timedelta(days=365),  # expires in 1 year
    "iat": datetime.now(timezone.utc),  # issued at
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(f"Demo user token: {token}")

# Test decoding
try:
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"Decoded payload: {decoded}")
    print("✅ Token is valid")
except Exception as e:
    print(f"❌ Token validation failed: {e}")
