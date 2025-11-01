import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config.settings import settings

print(f"Secret key: {settings.secret_key}")
print(f"Algorithm: {settings.algorithm}")
print(f"MongoDB URI: {settings.mongodb_uri}")
print(f"Database name: {settings.database_name}")
