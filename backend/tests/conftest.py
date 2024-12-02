from dotenv import load_dotenv
import sys
from pathlib import Path

load_dotenv()

# Add the backend directory to sys.path if not already present
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
