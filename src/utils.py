# src/utils.py
import hashlib
import uuid
from datetime import datetime

def hash_password(password):
    """
    Hashes a password using SHA-256.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password, hashed_password):
    """
    Verifies a plain password against its hashed version.
    """
    return hash_password(plain_password) == hashed_password

def generate_unique_id():
    """
    Generates a short, unique ID.
    """
    return str(uuid.uuid4())[:8]

def get_current_date_str():
    """
    Returns the current date as a string in YYYY-MM-DD format.
    """
    return datetime.now().strftime('%Y-%m-%d')
