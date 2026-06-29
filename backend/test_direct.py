import os
import sys
from dotenv import load_dotenv

# Ensure dotenv is loaded pointing specifically to backend/.env with override=True
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path, override=True)

from app import app
from config import Config
from routes.tasks import create_task

print("Starting direct task creation check...")
active_key = Config.GEMINI_API_KEY
print("Gemini_api_key present in process env:", bool(os.getenv("Gemini_api_key")))
print("GEMINI_API_KEY present in process env:", bool(os.getenv("GEMINI_API_KEY")))
if active_key:
    print("Active API Key last 4 characters:", f"...{active_key[-4:]}")
else:
    print("Active API Key: None")
print("GEMINI_MODEL present:", os.getenv("GEMINI_MODEL"))

with app.app_context():
    with app.test_request_context(json={
        "title": "Build a Flask Backend MVP",
        "description": "Create SQLite models, write Flask routers, connect to Gemini, and write tests.",
        "deadline": "2026-06-30T12:00:00"
    }):
        try:
            res = create_task()
            if isinstance(res, tuple):
                response, status_code = res
                print("Status Code:", status_code)
                print("Response:", response.get_json())
            else:
                print("Response:", res.get_json())
        except Exception as e:
            import traceback
            print("OUTER EXCEPTION CAUGHT:")
            traceback.print_exc()
