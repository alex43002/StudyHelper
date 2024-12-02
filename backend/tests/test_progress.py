from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
import json

client = TestClient(app)
PROGRESS_FILE = Path("storage/progress.json")

def reset_file(file_path, content):
    file_path.write_text(encrypt_data(json.dumps(content)))

def test_get_progress():
    reset_file(PROGRESS_FILE, {})
    response = client.get("/progress")
    assert response.status_code == 200
    assert response.json() == {}

def test_update_progress():
    reset_file(PROGRESS_FILE, {})
    update_data = {"study_time": 60, "tasks_completed": 1}
    response = client.post("/progress", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Progress updated successfully"}

    progress = client.get("/progress").json()
    assert progress["study_time"] == 60
    assert progress["tasks_completed"] == 1
