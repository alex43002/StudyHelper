from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
import json

client = TestClient(app)
TIMER_FILE = Path("storage/timer.json")


def reset_file(file_path, content):
    """
    Reset the file with encrypted content for testing.
    """
    file_path.write_text(encrypt_data(json.dumps(content)))


def test_timer():
    """
    Test the timer functionality including start, pause, complete, and status checks.
    """
    # Reset the timer file
    reset_file(
        TIMER_FILE,
        {"status": "idle", "start_time": None, "duration": 0, "logs": []},
    )

    # Start timer with a valid duration
    response = client.post("/timer/start", json={"duration": 25})
    assert response.status_code == 200, "Expected status code 200 for starting the timer"
    assert response.json()["message"] == "Timer started"

    # Attempt to start the timer while it is already active
    response = client.post("/timer/start", json={"duration": 30})
    assert response.status_code == 400, "Expected status code 400 for starting an active timer"
    assert response.json()["detail"] == "Timer is already running"

    # Pause the active timer
    response = client.post("/timer/pause")
    assert response.status_code == 200, "Expected status code 200 for pausing the timer"
    assert response.json()["message"] == "Timer paused"

    # Resume the paused timer
    response = client.post("/timer/start", json={"duration": 10})
    assert response.status_code == 200, "Expected status code 200 for resuming the timer"
    assert response.json()["message"] == "Timer started"

    # Complete the active timer
    response = client.post("/timer/complete")
    assert response.status_code == 200, "Expected status code 200 for completing the timer"
    assert response.json()["message"] == "Timer completed"

    # Attempt to complete a timer when idle
    response = client.post("/timer/complete")
    assert response.status_code == 400, "Expected status code 400 for completing an idle timer"
    assert response.json()["detail"] == "No active timer to complete"

    # Attempt to pause a timer when idle
    response = client.post("/timer/pause")
    assert response.status_code == 400, "Expected status code 400 for pausing an idle timer"
    assert response.json()["detail"] == "No active timer to pause"

    # Check the timer status after resetting
    response = client.get("/timer/status")
    assert response.status_code == 200, "Expected status code 200 for checking timer status"
    status = response.json()
    assert status["status"] == "idle", "Expected timer status to be 'idle'"
    assert status["start_time"] is None, "Expected no start time for idle timer"
    assert status["duration"] == 0, "Expected duration to be 0 for idle timer"
    assert isinstance(status["logs"], list), "Timer logs should be a list"


def test_timer_logs():
    """
    Test the log functionality of the timer.
    """
    # Reset the timer file
    reset_file(
        TIMER_FILE,
        {"status": "idle", "start_time": None, "duration": 0, "logs": []},
    )

    # Start and complete a timer to generate logs
    client.post("/timer/start", json={"duration": 15})
    client.post("/timer/complete")

    # Check the logs
    response = client.get("/timer/status")
    assert response.status_code == 200, "Expected status code 200 for checking timer status"
    status = response.json()
    assert len(status["logs"]) == 1, "Expected one log entry after completing one timer"
    log_entry = status["logs"][0]
    assert "start_time" in log_entry, "Log entry should include 'start_time'"
    assert "end_time" in log_entry, "Log entry should include 'end_time'"
    assert log_entry["duration"] == 15, "Log entry duration should match the completed timer"

    # Start and complete another timer
    client.post("/timer/start", json={"duration": 20})
    client.post("/timer/complete")

    # Verify that logs are accumulating
    response = client.get("/timer/status")
    logs = response.json()["logs"]
    assert len(logs) == 2, "Expected two log entries after completing two timers"
    assert logs[-1]["duration"] == 20, "Latest log entry duration should match the last timer completed"
