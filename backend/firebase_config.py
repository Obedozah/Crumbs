import firebase_admin
from firebase_admin import firestore
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(env_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()