import os
import dotenv

# Determine path to the local backend/.env file
backend_dir = os.path.dirname(__file__)
env_path = os.path.join(backend_dir, '.env')

# 1. Load the env file with override=True to allow local .env values to override existing process environment variables
if os.path.exists(env_path):
    dotenv.load_dotenv(dotenv_path=env_path, override=True)
else:
    dotenv.load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'questflow-dev-secret-key-1337')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///questflow.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. Specifically retrieve keys from the local .env file first, falling back to process env only if not found
    local_env_values = dotenv.dotenv_values(env_path) if os.path.exists(env_path) else {}
    GEMINI_API_KEY = (
        local_env_values.get("Gemini_api_key") or 
        local_env_values.get("GEMINI_API_KEY") or 
        os.environ.get("Gemini_api_key") or 
        os.environ.get("GEMINI_API_KEY")
    )
