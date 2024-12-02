from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
from tests.helpers import reset_file, cleanup_files  # Import helper functions
import json

client = TestClient(app)

PROGRESS_FILE = Path("storage/progress.json")


def test_get_progress():
    # Reset the progress file to an empty dictionary
    reset_file(PROGRESS_FILE, {})
    response = client.get("/progress")
    assert response.status_code == 200
    assert response.json() == {}

    # Validate response structure
    assert isinstance(response.json(), dict)


def test_update_progress():
    reset_file(PROGRESS_FILE, {})

    # Update progress with valid data
    update_data = {"study_time": 60, "tasks_completed": 1}
    response = client.post("/progress", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Progress updated successfully"}

    # Verify progress update
    progress = client.get("/progress").json()
    assert progress["study_time"] == 60
    assert progress["tasks_completed"] == 1

    # Update progress with additional data
    additional_update = {"study_time": 30, "tasks_completed": 2}
    response = client.post("/progress", json=additional_update)
    assert response.status_code == 200
    assert response.json() == {"message": "Progress updated successfully"}

    # Verify cumulative progress
    progress = client.get("/progress").json()
    assert progress["study_time"] == 90  # 60 + 30
    assert progress["tasks_completed"] == 3  # 1 + 2

    # Handle edge cases
    invalid_update = {"study_time": "invalid", "tasks_completed": -1}
    response = client.post("/progress", json=invalid_update)
    assert response.status_code == 422, "Expected status code 422 for invalid data types or negative values"

