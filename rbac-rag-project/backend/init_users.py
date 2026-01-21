import sqlite3
from backend.database import get_connection
from backend.jwt_utils import hash_password

def init_users():
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    users = [
        ("admin", hash_password("admin123"), "Admin"),
        ("finance1", hash_password("finance123"), "Finance"),
        ("hr1", hash_password("hr123"), "HR"),
        ("employee1", hash_password("emp123"), "Employee"),
        ("ceo", hash_password("ceo123"), "C-Level"),
    ]

    for user in users:
        cursor.execute(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
            user
        )

    conn.commit()
    conn.close()
    print("✅ Users initialized successfully")

if __name__ == "__main__":
    init_users()
