import random
from fastapi import FastAPI, HTTPException, UploadFile
from pathlib import Path
import json
from utils import encrypt_data, decrypt_data
import zipfile
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

class TimerStartRequest(BaseModel):
    duration: int

class Task(BaseModel):
    title: str
    description: str

class ProgressUpdate(BaseModel):
    study_time: int = Field(..., ge=0, description="Study time in minutes")
    tasks_completed: int = Field(..., ge=0, description="Number of tasks completed")


app = FastAPI()

STORAGE_DIR = Path("storage")


TASKS_FILE = STORAGE_DIR / "tasks.json"
PROGRESS_FILE = STORAGE_DIR / "progress.json"
TIMER_FILE = STORAGE_DIR / "timer.json"
FLASHCARDS_FILE = STORAGE_DIR / "flashcards.json"
SETTINGS_FILE = STORAGE_DIR / "settings.json"

# Ensure storage directory and task/progress files exist
STORAGE_DIR.mkdir(exist_ok=True)

# Ensure the settings file exists
if not SETTINGS_FILE.exists():
    SETTINGS_FILE.write_text(encrypt_data(json.dumps({"storage_path": str(STORAGE_DIR)})))

# Ensure the flashcards file exists
if not FLASHCARDS_FILE.exists():
    FLASHCARDS_FILE.write_text(encrypt_data(json.dumps([])))  # Empty flashcards list

# Ensure the timer file exists
if not TIMER_FILE.exists():
    TIMER_FILE.write_text(encrypt_data(json.dumps({"status": "idle", "start_time": None, "duration": 0, "logs": []})))

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
def add_task(task: Task):
    tasks = json.loads(decrypt_data(TASKS_FILE.read_text()))
    tasks.append(task.dict())
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
def update_progress(update: ProgressUpdate):
    progress = json.loads(decrypt_data(PROGRESS_FILE.read_text()))
    for key, value in update.model_dump().items():
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

@app.post("/timer/start")
def start_timer(request: TimerStartRequest):
    timer_data = json.loads(decrypt_data(TIMER_FILE.read_text()))
    if timer_data["status"] == "active":
        raise HTTPException(status_code=400, detail="Timer is already running")

    timer_data["status"] = "active"
    timer_data["start_time"] = datetime.now().isoformat()
    timer_data["duration"] = request.duration
    TIMER_FILE.write_text(encrypt_data(json.dumps(timer_data, indent=4)))
    return {"message": "Timer started"}

@app.post("/timer/pause")
def pause_timer():
    timer_data = json.loads(decrypt_data(TIMER_FILE.read_text()))
    if timer_data["status"] != "active":
        raise HTTPException(status_code=400, detail="No active timer to pause")

    elapsed_time = (datetime.now() - datetime.fromisoformat(timer_data["start_time"])).total_seconds()
    timer_data["status"] = "paused"
    timer_data["duration"] = max(0, timer_data["duration"] - elapsed_time)
    TIMER_FILE.write_text(encrypt_data(json.dumps(timer_data, indent=4)))
    return {"message": "Timer paused"}

@app.post("/timer/complete")
def complete_timer():
    timer_data = json.loads(decrypt_data(TIMER_FILE.read_text()))
    if timer_data["status"] != "active":
        raise HTTPException(status_code=400, detail="No active timer to complete")

    end_time = datetime.now().isoformat()
    log_entry = {
        "start_time": timer_data["start_time"],
        "end_time": end_time,
        "duration": timer_data["duration"],
    }
    timer_data["logs"].append(log_entry)
    timer_data["status"] = "idle"
    timer_data["start_time"] = None
    timer_data["duration"] = 0
    TIMER_FILE.write_text(encrypt_data(json.dumps(timer_data, indent=4)))
    return {"message": "Timer completed"}


@app.get("/timer/status")
def get_timer_status():
    timer_data = json.loads(decrypt_data(TIMER_FILE.read_text()))
    return timer_data

@app.get("/flashcards")
def get_flashcards():
    flashcards = decrypt_data(FLASHCARDS_FILE.read_text())
    return json.loads(flashcards)

@app.post("/flashcards")
def add_flashcard(flashcard: dict):
    flashcards = json.loads(decrypt_data(FLASHCARDS_FILE.read_text()))
    flashcards.append(flashcard)
    FLASHCARDS_FILE.write_text(encrypt_data(json.dumps(flashcards, indent=4)))
    return {"message": "Flashcard added successfully"}

@app.put("/flashcards/{flashcard_id}")
def update_flashcard(flashcard_id: int, flashcard: dict):
    flashcards = json.loads(decrypt_data(FLASHCARDS_FILE.read_text()))
    if flashcard_id < 0 or flashcard_id >= len(flashcards):
        raise HTTPException(status_code=404, detail="Flashcard not found")
    flashcards[flashcard_id] = flashcard
    FLASHCARDS_FILE.write_text(encrypt_data(json.dumps(flashcards, indent=4)))
    return {"message": "Flashcard updated successfully"}

@app.delete("/flashcards/{flashcard_id}")
def delete_flashcard(flashcard_id: int):
    flashcards = json.loads(decrypt_data(FLASHCARDS_FILE.read_text()))
    if flashcard_id < 0 or flashcard_id >= len(flashcards):
        raise HTTPException(status_code=404, detail="Flashcard not found")
    flashcards.pop(flashcard_id)
    FLASHCARDS_FILE.write_text(encrypt_data(json.dumps(flashcards, indent=4)))
    return {"message": "Flashcard deleted successfully"}

@app.get("/flashcards/quiz")
def quiz_flashcards(count: int = 5):
    flashcards = json.loads(decrypt_data(FLASHCARDS_FILE.read_text()))
    if not flashcards:
        raise HTTPException(status_code=404, detail="No flashcards available")
    return random.sample(flashcards, min(count, len(flashcards)))

@app.get("/settings")
def get_settings():
    settings = decrypt_data(SETTINGS_FILE.read_text())
    return json.loads(settings)

@app.post("/settings")
def update_settings(new_settings: dict):
    settings = json.loads(decrypt_data(SETTINGS_FILE.read_text()))
    settings.update(new_settings)
    SETTINGS_FILE.write_text(encrypt_data(json.dumps(settings, indent=4)))
    return {"message": "Settings updated successfully"}

