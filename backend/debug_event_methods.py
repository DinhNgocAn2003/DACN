# debug_event_methods.py
# Run from repository root with: python backend\debug_event_methods.py
from fastapi.testclient import TestClient
import os
import sys

# Ensure backend package is importable
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import app

client = TestClient(app)

paths = ["/events", "/events/1", "/events/user/1"]
methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

# Minimal payload for POST/PUT
payload = {
    "user_id": 1,
    "event_name": "Test Event",
    "start_time": "2025-11-13T10:00:00",
    "end_time": "2025-11-13T11:00:00",
    "location": "Test",
    "time_reminder": 15
}

print('Testing methods on event-related paths')
for path in paths:
    print('\nPath:', path)
    for method in methods:
        try:
            if method == 'GET':
                r = client.get(path)
            elif method == 'POST':
                r = client.post(path, json=payload)
            elif method == 'PUT':
                r = client.put(path, json=payload)
            elif method == 'DELETE':
                r = client.delete(path)
            elif method == 'OPTIONS':
                r = client.options(path)
            else:
                continue

            allow = r.headers.get('allow')
            print(f" {method}: {r.status_code} Allow={allow}")
        except Exception as exc:
            print(f" {method}: Exception -> {exc}")
