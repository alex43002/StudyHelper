from pathlib import Path
from utils import encrypt_data
import json

# Directory and files to manage
STORAGE_DIR = Path("storage")
FILES_TO_CLEANUP = [
    "tasks.json",
    "progress.json",
    "timer.json",
    "flashcards.json",
    "settings.json",
    "data_export.zip",
    "test_import.zip",
    "encryption_key",
]

def cleanup_files():
    """
    Deletes specified test files in the storage directory if they exist.
    """
    for file_name in FILES_TO_CLEANUP:
        file_path = STORAGE_DIR / file_name
        if file_path.exists():
            file_path.unlink()

def reset_file(file_path: Path, content: dict | list):
    """
    Resets the content of a file with encrypted JSON data.
    """
    STORAGE_DIR.mkdir(exist_ok=True)  # Ensure storage directory exists
    file_path.write_text(encrypt_data(json.dumps(content)))

def reset_all_files():
    """
    Resets all storage files to their default states.
    """
    reset_file(STORAGE_DIR / "tasks.json", [])
    reset_file(STORAGE_DIR / "progress.json", {})
    reset_file(
        STORAGE_DIR / "timer.json",
        {"status": "idle", "start_time": None, "duration": 0, "logs": []},
    )
    reset_file(STORAGE_DIR / "flashcards.json", [])
    reset_file(
        STORAGE_DIR / "settings.json",
        {"storage_path": str(STORAGE_DIR), "theme": "light", "notifications": True},
    )
