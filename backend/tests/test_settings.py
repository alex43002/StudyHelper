from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
import json

client = TestClient(app)
SETTINGS_FILE = Path("storage/settings.json")

def reset_file(file_path, content):
    file_path.write_text(encrypt_data(json.dumps(content)))

def test_settings():
    reset_file(
        SETTINGS_FILE,
        {"storage_path": "storage", "theme": "light", "notifications": True},
    )

    response = client.get("/settings")
    assert response.status_code == 200

    new_settings = {"theme": "dark"}
    response = client.post("/settings", json=new_settings)
    assert response.status_code == 200
