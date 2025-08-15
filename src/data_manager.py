# src/data_manager.py
import json
import os

# The absolute path to the 'data' directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Define file paths for easier management
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
COURSES_FILE = os.path.join(DATA_DIR, 'courses.json')
PROPOSALS_FILE = os.path.join(DATA_DIR, 'thesis_proposals.json')
THESES_FILE = os.path.join(DATA_DIR, 'theses.json')

def read_data(file_path):
    """
    Reads data from a JSON file.
    Returns an empty list if the file is empty or does not exist.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_data(file_path, data):
    """
    Writes data to a JSON file with pretty printing.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Helper functions for specific data types ---

def get_users():
    """Fetches all users."""
    return read_data(USERS_FILE)

def get_courses():
    """Fetches all courses."""
    return read_data(COURSES_FILE)

def get_proposals():
    """Fetches all thesis proposals."""
    return read_data(PROPOSALS_FILE)

def get_theses():
    """Fetches all final theses."""
    return read_data(THESES_FILE)

def save_users(users):
    """Saves the users list to its file."""
    write_data(USERS_FILE, users)

def save_courses(courses):
    """Saves the courses list to its file."""
    write_data(COURSES_FILE, courses)

def save_proposals(proposals):
    """Saves the proposals list to its file."""
    write_data(PROPOSALS_FILE, proposals)

def save_theses(theses):
    """Saves the theses list to its file."""
    write_data(THESES_FILE, theses)
