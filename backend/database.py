
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "vazhikaatti.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add new columns if an older complaints table already exists
    cursor.execute("PRAGMA table_info(complaints)")
    existing_columns = [row["name"] for row in cursor.fetchall()]

    if "name" not in existing_columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN name TEXT")

    if "email" not in existing_columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN email TEXT")

    # Services table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            description TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM services")
    count = cursor.fetchone()[0]

    if count == 0:
        services = [
            ("Local Services", "Find local public services"),
            ("Community Updates", "View community announcements"),
            ("Report Issues", "Report local public problems"),
            ("Connect People", "Connect with your community")
        ]

        cursor.executemany(
            "INSERT INTO services (service_name, description) VALUES (?, ?)",
            services
        )

    conn.commit()
    conn.close()
