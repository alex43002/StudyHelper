from main import app
from fastapi.testclient import TestClient
from pathlib import Path
from utils import encrypt_data
from tests.helpers import reset_file, cleanup_files 
import json

client = TestClient(app)

FLASHCARDS_FILE = Path("storage/flashcards.json")


def test_flashcards():
    # Reset flashcards file
    reset_file(FLASHCARDS_FILE, [])

    # Add a flashcard
    flashcard = {"question": "What is FastAPI?", "answer": "A Python framework"}
    response = client.post("/flashcards", json=flashcard)
    assert response.status_code == 200
    assert response.json() == {"message": "Flashcard added successfully"}

    # Retrieve all flashcards
    response = client.get("/flashcards")
    assert response.status_code == 200
    flashcards = response.json()
    assert len(flashcards) == 1
    assert flashcards[0]["question"] == "What is FastAPI?"

    # Update the flashcard
    updated_flashcard = {"question": "What is FastAPI?", "answer": "A web framework"}
    response = client.put("/flashcards/0", json=updated_flashcard)
    assert response.status_code == 200
    assert response.json() == {"message": "Flashcard updated successfully"}

    # Verify the update
    response = client.get("/flashcards")
    flashcards = response.json()
    assert flashcards[0]["answer"] == "A web framework"

    # Delete the flashcard
    response = client.delete("/flashcards/0")
    assert response.status_code == 200
    assert response.json() == {"message": "Flashcard deleted successfully"}

    # Verify deletion
    response = client.get("/flashcards")
    assert response.status_code == 200
    flashcards = response.json()
    assert len(flashcards) == 0

    # Attempt to delete a non-existent flashcard
    response = client.delete("/flashcards/0")
    assert response.status_code == 404
    assert response.json()["detail"] == "Flashcard not found"

    # Clean up after test
    cleanup_files()
