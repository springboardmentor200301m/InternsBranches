import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "users.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, password, role FROM users WHERE username=?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "username": row[0],
        "password": row[1],
        "role": row[2]
    }
