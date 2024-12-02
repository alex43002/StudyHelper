from main import app
from fastapi.testclient import TestClient
from pathlib import Path
import json
import zipfile
from utils import encrypt_data, decrypt_data

client = TestClient(app)

# Paths for testing
TASKS_FILE = Path("storage/tasks.json")
PROGRESS_FILE = Path("storage/progress.json")
EXPORT_FILE = Path("storage/data_export.zip")
IMPORT_FILE = Path("storage/test_import.zip")


# Helper function to reset files with encrypted data
def reset_file(file_path, content):
    file_path.write_text(encrypt_data(json.dumps(content)))


# Root endpoint
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is working"}


# Tasks endpoints
def test_get_tasks():
    # Ensure tasks file is empty initially
    reset_file(TASKS_FILE, [])
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json() == []

def test_add_task():
    reset_file(TASKS_FILE, [])
    task = {"title": "Test Task", "description": "Test Description"}
    response = client.post("/tasks", json=task)
    assert response.status_code == 200
    assert response.json() == {"message": "Task added successfully"}

    # Verify the task was added
    tasks_response = client.get("/tasks")
    tasks = tasks_response.json()
    assert len(tasks) == 1
    assert tasks[-1] == task

def test_delete_task():
    # Add a task to ensure there is one to delete
    reset_file(TASKS_FILE, [{"title": "Task to Delete", "description": "Will be deleted"}])

    # Get the index of the task to delete
    tasks_response = client.get("/tasks")
    task_id = len(tasks_response.json()) - 1

    # Delete the task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Task deleted successfully"}

    # Verify it was deleted
    tasks_after_delete = client.get("/tasks").json()
    assert len(tasks_after_delete) == 0


# Progress endpoints
def test_get_progress():
    # Ensure progress file is empty initially
    reset_file(PROGRESS_FILE, {})
    response = client.get("/progress")
    assert response.status_code == 200
    assert response.json() == {}

def test_update_progress():
    reset_file(PROGRESS_FILE, {})
    # Update progress with new data
    update_data = {"study_time": 60, "tasks_completed": 1}
    response = client.post("/progress", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Progress updated successfully"}

    # Verify the progress was updated
    progress_response = client.get("/progress")
    progress = progress_response.json()
    assert progress["study_time"] == 60
    assert progress["tasks_completed"] == 1


# Export endpoint
def test_export_data():
    reset_file(TASKS_FILE, [{"title": "Test Task"}])
    reset_file(PROGRESS_FILE, {"study_time": 60})

    # Call the export endpoint
    response = client.get("/export")
    assert response.status_code == 200
    assert "Data exported successfully" in response.json()["message"]

    # Verify the export file exists
    assert EXPORT_FILE.exists()

    # Check the contents of the ZIP file
    with zipfile.ZipFile(EXPORT_FILE, "r") as zipf:
        files = zipf.namelist()
        assert "tasks.json" in files
        assert "progress.json" in files

    # Clean up the exported file
    EXPORT_FILE.unlink()


# Import endpoint
def test_import_data():
    # Prepare a test ZIP file with sample JSON data
    with zipfile.ZipFile(IMPORT_FILE, "w") as zipf:
        zipf.writestr("tasks.json", encrypt_data(json.dumps([{"title": "Imported Task"}])))
        zipf.writestr("progress.json", encrypt_data(json.dumps({"study_time": 120})))

    # Simulate file upload
    with open(IMPORT_FILE, "rb") as f:
        response = client.post("/import", files={"file": ("test_import.zip", f, "application/zip")})
    assert response.status_code == 200
    assert response.json() == {"message": "Data imported successfully"}

    # Verify the imported data
    tasks_response = client.get("/tasks")
    tasks = tasks_response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Imported Task"

    progress_response = client.get("/progress")
    progress = progress_response.json()
    assert progress["study_time"] == 120

    # Clean up test files
    IMPORT_FILE.unlink()
