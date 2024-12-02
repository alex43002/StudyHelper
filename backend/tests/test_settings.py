from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data, decrypt_data
import json

client = TestClient(app)
SETTINGS_FILE = Path("storage/settings.json")


def reset_file(file_path, content):
    """
    Reset the file with encrypted content.
    """
    file_path.write_text(encrypt_data(json.dumps(content)))


def test_get_settings():
    """
    Test retrieving settings with default values.
    """
    default_settings = {
        "storage_path": "storage",
        "theme": "light",
        "notifications": True,
    }
    reset_file(SETTINGS_FILE, default_settings)

    response = client.get("/settings")
    assert response.status_code == 200, "Expected status code 200 for GET /settings"
    assert response.json() == default_settings, "Unexpected settings data retrieved"


def test_update_settings():
    """
    Test updating specific settings and ensuring changes persist.
    """
    default_settings = {
        "storage_path": "storage",
        "theme": "light",
        "notifications": True,
    }
    reset_file(SETTINGS_FILE, default_settings)

    # Update theme and notifications
    new_settings = {"theme": "dark", "notifications": False}
    response = client.post("/settings", json=new_settings)
    assert response.status_code == 200, "Expected status code 200 for POST /settings"
    assert response.json() == {"message": "Settings updated successfully"}

    # Verify updated settings
    response = client.get("/settings")
    updated_settings = response.json()
    assert updated_settings["theme"] == "dark", "Theme setting not updated correctly"
    assert updated_settings["notifications"] is False, "Notifications setting not updated correctly"

    # Ensure other settings remain unchanged
    assert updated_settings["storage_path"] == "storage", "Unexpected change to storage_path"


def test_invalid_update_settings():
    """
    Test handling of invalid settings data.
    """
    reset_file(
        SETTINGS_FILE,
        {"storage_path": "storage", "theme": "light", "notifications": True},
    )

    # Attempt to update with invalid data (non-dict format)
    response = client.post("/settings", json=["invalid", "data"])
    assert response.status_code == 422, "Expected status code 422 for invalid payload"

    # Ensure no changes were made to settings
    response = client.get("/settings")
    settings = response.json()
    assert settings["theme"] == "light", "Settings were unexpectedly altered"


def test_settings_edge_cases():
    """
    Test edge cases such as partial updates and empty payload.
    """
    reset_file(
        SETTINGS_FILE,
        {"storage_path": "storage", "theme": "light", "notifications": True},
    )

    # Partial update
    response = client.post("/settings", json={"theme": "dark"})
    assert response.status_code == 200, "Expected status code 200 for partial update"
    assert response.json() == {"message": "Settings updated successfully"}

    # Verify partial update
    response = client.get("/settings")
    settings = response.json()
    assert settings["theme"] == "dark", "Theme setting not updated correctly"
    assert settings["notifications"] is True, "Notifications setting unexpectedly changed"

    # Attempt to update with an empty payload
    response = client.post("/settings", json={})
    assert response.status_code == 200, "Expected status code 200 for empty payload"
    assert response.json() == {"message": "Settings updated successfully"}

    # Verify no changes were made
    response = client.get("/settings")
    settings = response.json()
    assert settings["theme"] == "dark", "Settings unexpectedly changed after empty payload"

