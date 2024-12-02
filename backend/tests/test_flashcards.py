from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
import json

client = TestClient(app)
FLASHCARDS_FILE = Path("storage/flashcards.json")

def reset_file(file_path, content):
    file_path.write_text(encrypt_data(json.dumps(content)))

def test_flashcards():
    reset_file(FLASHCARDS_FILE, [])

    flashcard = {"question": "What is FastAPI?", "answer": "A Python framework"}
    response = client.post("/flashcards", json=flashcard)
    assert response.status_code == 200

    response = client.get("/flashcards")
    assert len(response.json()) == 1
