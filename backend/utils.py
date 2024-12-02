from pathlib import Path
from cryptography.fernet import Fernet

# Path to encryption key
STORAGE_DIR = Path("storage")
ENCRYPTION_KEY_FILE = STORAGE_DIR / "encryption_key"

# Ensure the storage directory exists
STORAGE_DIR.mkdir(exist_ok=True)

# Load or create the encryption key
if not ENCRYPTION_KEY_FILE.exists():
    key = Fernet.generate_key()
    ENCRYPTION_KEY_FILE.write_bytes(key)
else:
    key = ENCRYPTION_KEY_FILE.read_bytes()

cipher = Fernet(key)

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    return cipher.decrypt(data.encode()).decode()
