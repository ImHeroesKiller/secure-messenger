import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'secure_messenger.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Encryption key (harus 32 byte untuk AES-256)
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your-32-byte-encryption-key-here!!')
