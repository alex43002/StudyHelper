from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
import json

client = TestClient(app)
TIMER_FILE = Path("storage/timer.json")

def reset_file(file_path, content):
    file_path.write_text(encrypt_data(json.dumps(content)))

def test_timer():
    reset_file(
        TIMER_FILE,
        {"status": "idle", "start_time": None, "duration": 0, "logs": []},
    )

    response = client.post("/timer/start", json={"duration": 25})
    assert response.status_code == 200
    assert response.json()["message"] == "Timer started"

    response = client.post("/timer/pause")
    assert response.status_code == 200
    assert response.json()["message"] == "Timer paused"
