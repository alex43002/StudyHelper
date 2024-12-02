from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
import json

client = TestClient(app)
TASKS_FILE = Path("storage/tasks.json")


def reset_file(file_path, content):
    """
    Reset the file with encrypted content for testing.
    """
    file_path.write_text(encrypt_data(json.dumps(content)))


def test_get_tasks():
    """
    Test retrieving tasks when the file is empty.
    """
    reset_file(TASKS_FILE, [])
    response = client.get("/tasks")
    assert response.status_code == 200, "Expected status code 200 for GET /tasks"
    assert isinstance(response.json(), list), "Tasks response should be a list"
    assert response.json() == [], "Tasks list should be empty"


def test_add_task():
    """
    Test adding a new task and verifying its addition.
    """
    reset_file(TASKS_FILE, [])
    task = {"title": "Test Task", "description": "Test Description"}

    response = client.post("/tasks", json=task)
    assert response.status_code == 200, "Expected status code 200 for POST /tasks"
    assert response.json() == {"message": "Task added successfully"}

    tasks = client.get("/tasks").json()
    assert len(tasks) == 1, "Expected exactly one task in the list"
    assert tasks[0] == task, "Added task does not match the input"


def test_add_task_invalid_payload():
    """
    Test adding a task with invalid payloads.
    """
    reset_file(TASKS_FILE, [])

    # Missing fields in the payload
    response = client.post("/tasks", json={"title": "Incomplete Task"})
    assert response.status_code == 422, "Expected status code 422 for invalid payload"

    # Invalid data types
    response = client.post(
        "/tasks", json={"title": 123, "description": ["invalid", "type"]}
    )
    assert response.status_code == 422, "Expected status code 422 for invalid payload"
    
    # Invalid data type in the payload
    response = client.post("/tasks", json={"title": 123, "description": True})
    assert response.status_code == 422, "Expected status code 422 for invalid data types"

    # Ensure no tasks were added
    tasks = client.get("/tasks").json()
    assert len(tasks) == 0, "No tasks should have been added with invalid payloads"


def test_delete_task():
    """
    Test deleting an existing task and verifying its removal.
    """
    reset_file(TASKS_FILE, [{"title": "Task to Delete", "description": "Will be deleted"}])
    task_id = len(client.get("/tasks").json()) - 1

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200, "Expected status code 200 for DELETE /tasks"
    assert response.json() == {"message": "Task deleted successfully"}

    tasks = client.get("/tasks").json()
    assert len(tasks) == 0, "Expected no tasks in the list after deletion"


def test_delete_task_invalid_id():
    """
    Test deleting a task with invalid task IDs.
    """
    reset_file(TASKS_FILE, [{"title": "Valid Task", "description": "Test Description"}])

    # Negative ID
    response = client.delete("/tasks/-1")
    assert response.status_code == 404, "Expected status code 404 for negative task ID"

    # Non-existent ID
    response = client.delete("/tasks/10")
    assert response.status_code == 404, "Expected status code 404 for non-existent task ID"

    # Ensure no tasks were deleted
    tasks = client.get("/tasks").json()
    assert len(tasks) == 1, "Task list should remain unchanged after invalid deletions"


def test_add_and_delete_multiple_tasks():
    """
    Test adding and deleting multiple tasks to ensure proper functionality.
    """
    reset_file(TASKS_FILE, [])

    # Add multiple tasks
    tasks_to_add = [
        {"title": "Task 1", "description": "First task"},
        {"title": "Task 2", "description": "Second task"},
        {"title": "Task 3", "description": "Third task"},
    ]
    for task in tasks_to_add:
        response = client.post("/tasks", json=task)
        assert response.status_code == 200, f"Failed to add task: {task['title']}"

    tasks = client.get("/tasks").json()
    assert len(tasks) == len(tasks_to_add), "Unexpected number of tasks after additions"

    # Delete tasks one by one
    for i in range(len(tasks_to_add)):
        response = client.delete(f"/tasks/{0}")  # Always delete the first task in the list
        assert response.status_code == 200, f"Failed to delete task with ID {i}"
        tasks = client.get("/tasks").json()
        assert len(tasks) == len(tasks_to_add) - (i + 1), "Unexpected number of tasks after deletion"
