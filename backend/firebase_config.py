import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(env_path)

if not firebase_admin._apps:
    credential_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credential_path:
        credential_path = Path(credential_path)
        if not credential_path.is_absolute():
            credential_path = env_path.parent / credential_path
        firebase_admin.initialize_app(
            credentials.Certificate(str(credential_path.resolve()))
        )
    else:
        firebase_admin.initialize_app()

db = firestore.client()
