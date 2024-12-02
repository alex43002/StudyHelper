from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
from tests.helpers import reset_file, cleanup_files
import json
import zipfile

client = TestClient(app)

TASKS_FILE = Path("storage/tasks.json")
PROGRESS_FILE = Path("storage/progress.json")
EXPORT_FILE = Path("storage/data_export.zip")
IMPORT_FILE = Path("storage/test_import.zip")


def test_export_data():
    # Reset files with test data
    reset_file(TASKS_FILE, [{"title": "Test Task"}])
    reset_file(PROGRESS_FILE, {"study_time": 60})

    # Call the export endpoint
    response = client.get("/export")
    assert response.status_code == 200
    assert EXPORT_FILE.exists()

    # Validate the contents of the exported ZIP file
    with zipfile.ZipFile(EXPORT_FILE, "r") as zipf:
        files = zipf.namelist()
        assert "tasks.json" in files
        assert "progress.json" in files

    # Clean up exported file
    cleanup_files()


def test_import_data():
    # Prepare a test ZIP file with encrypted JSON data
    with zipfile.ZipFile(IMPORT_FILE, "w") as zipf:
        zipf.writestr("tasks.json", encrypt_data(json.dumps([{"title": "Imported Task"}])))
        zipf.writestr("progress.json", encrypt_data(json.dumps({"study_time": 120})))

    # Simulate uploading the ZIP file to the import endpoint
    with open(IMPORT_FILE, "rb") as f:
        response = client.post("/import", files={"file": ("test_import.zip", f, "application/zip")})
    assert response.status_code == 200

    # Validate imported data
    tasks = client.get("/tasks").json()
    assert tasks[0]["title"] == "Imported Task"

    progress = client.get("/progress").json()
    assert progress["study_time"] == 120

    # Clean up test files
    cleanup_files()
