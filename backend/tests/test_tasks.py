from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
import json

client = TestClient(app)
TASKS_FILE = Path("storage/tasks.json")

def reset_file(file_path, content):
    file_path.write_text(encrypt_data(json.dumps(content)))

def test_get_tasks():
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

    tasks = client.get("/tasks").json()
    assert len(tasks) == 1
    assert tasks[0] == task

def test_delete_task():
    reset_file(TASKS_FILE, [{"title": "Task to Delete", "description": "Will be deleted"}])
    task_id = len(client.get("/tasks").json()) - 1

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}

    tasks = client.get("/tasks").json()
    assert len(tasks) == 0
