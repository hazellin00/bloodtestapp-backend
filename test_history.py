import urllib.request
import json
from datetime import datetime

url = "http://localhost:8000/api/history/dad-001/2026-03-03"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("Success! Data:", json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print("Error fetching:", e)
