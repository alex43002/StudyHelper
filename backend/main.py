from fastapi import FastAPI, HTTPException, UploadFile
from pathlib import Path
import json
from utils import encrypt_data, decrypt_data
import zipfile

app = FastAPI()

STORAGE_DIR = Path("storage")
TASKS_FILE = STORAGE_DIR / "tasks.json"
PROGRESS_FILE = STORAGE_DIR / "progress.json"

# Ensure storage directory and task/progress files exist
STORAGE_DIR.mkdir(exist_ok=True)

# Initialize files if they don't exist
if not TASKS_FILE.exists():
    TASKS_FILE.write_text(encrypt_data("[]"))  # Empty encrypted task list

if not PROGRESS_FILE.exists():
    PROGRESS_FILE.write_text(encrypt_data("{}"))  # Empty encrypted progress data

@app.get("/")
def read_root():
    return {"message": "Backend is working"}

@app.get("/tasks")
def get_tasks():
    tasks = decrypt_data(TASKS_FILE.read_text())
    return json.loads(tasks)

@app.post("/tasks")
def add_task(task: dict):
    tasks = json.loads(decrypt_data(TASKS_FILE.read_text()))
    tasks.append(task)
    TASKS_FILE.write_text(encrypt_data(json.dumps(tasks, indent=4)))
    return {"message": "Task added successfully"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = json.loads(decrypt_data(TASKS_FILE.read_text()))
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    tasks.pop(task_id)
    TASKS_FILE.write_text(encrypt_data(json.dumps(tasks, indent=4)))
    return {"message": "Task deleted successfully"}

@app.get("/progress")
def get_progress():
    progress = decrypt_data(PROGRESS_FILE.read_text())
    return json.loads(progress)

@app.post("/progress")
def update_progress(update: dict):
    progress = json.loads(decrypt_data(PROGRESS_FILE.read_text()))
    for key, value in update.items():
        progress[key] = progress.get(key, 0) + value
    PROGRESS_FILE.write_text(encrypt_data(json.dumps(progress, indent=4)))
    return {"message": "Progress updated successfully"}

@app.get("/export")
def export_data():
    export_file = STORAGE_DIR / "data_export.zip"
    with zipfile.ZipFile(export_file, "w") as zipf:
        for file in STORAGE_DIR.glob("*.json"):
            zipf.write(file, file.name)
    return {"message": f"Data exported successfully. File: {export_file}"}

@app.post("/import")
def import_data(file: UploadFile):
    # Save uploaded file temporarily
    temp_file = STORAGE_DIR / "uploaded_data.zip"
    with open(temp_file, "wb") as f:
        f.write(file.file.read())

    # Validate and extract uploaded ZIP file
    try:
        with zipfile.ZipFile(temp_file, "r") as zipf:
            zipf.extractall(STORAGE_DIR)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    finally:
        temp_file.unlink()  # Clean up temporary file

    return {"message": "Data imported successfully"}
