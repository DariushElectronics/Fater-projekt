# scripts/seed_data.py
import sys
import os

# Add the project root to the Python path to allow importing from 'src'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src import data_manager
from src import utils

def seed():
    """
    Populates the database with initial sample data.
    This will overwrite existing data.
    """
    print("Seeding database with initial data...")

    # --- Clear existing data ---
    data_manager.save_users([])
    data_manager.save_courses([])
    data_manager.save_proposals([])
    data_manager.save_theses([])

    # --- Create Sample Users ---
    users = [
        # Professors
        {
            "id": "prof101", "name": "دکتر اکبری", "role": "professor",
            "password_hash": utils.hash_password("pass123")
        },
        {
            "id": "prof102", "name": "دکتر صالحی", "role": "professor",
            "password_hash": utils.hash_password("pass456")
        },
        # Students
        {
            "id": "stu981001", "name": "مریم رضایی", "role": "student",
            "password_hash": utils.hash_password("student1")
        },
        {
            "id": "stu981002", "name": "علی محمدی", "role": "student",
            "password_hash": utils.hash_password("student2")
        },
        {
            "id": "stu981003", "name": "زهرا حسینی", "role": "student",
            "password_hash": utils.hash_password("student3")
        }
    ]
    data_manager.save_users(users)
    print(f"-> {len(users)} users created.")

    # --- Create Sample Courses ---
    courses = [
        {
            "id": "CRS01", "title": "پایان‌نامه - هوش مصنوعی", "professor_id": "prof101",
            "year": 1404, "semester": "نیمسال اول", "capacity": 3,
            "resources": "مقالات IEEE", "sessions": 10, "credits": 6
        },
        {
            "id": "CRS02", "title": "پایان‌نامه - شبکه‌های کامپیوتری", "professor_id": "prof102",
            "year": 1404, "semester": "نیمسال اول", "capacity": 2,
            "resources": "کتاب مرجع شبکه", "sessions": 10, "credits": 6
        },
        {
            "id": "CRS03", "title": "پایان‌نامه - پردازش تصویر", "professor_id": "prof101",
            "year": 1404, "semester": "نیمسال دوم", "capacity": 2,
            "resources": "کتاب گونزالس", "sessions": 12, "credits": 6
        }
    ]
    data_manager.save_courses(courses)
    print(f"-> {len(courses)} courses created.")

    print("\nDatabase seeding complete!")

if __name__ == "__main__":
    seed()
