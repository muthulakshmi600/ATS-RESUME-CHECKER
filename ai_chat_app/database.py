"""
Database module for AI Chat Application.
Manages SQLite database schema, connections, and migrations.
"""

import os
import sqlite3
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "ai_chat.db")

os.makedirs(DATA_DIR, exist_ok=True)


def get_db():
    """Returns a thread-safe connection to the SQLite database with row factory."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db()
    with conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                avatar TEXT DEFAULT 'avatar-1',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                settings_json TEXT DEFAULT '{}'
            );
        """)

        # Schema migrations for users table if existing database is missing columns
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        existing_user_cols = [row["name"] for row in cursor.fetchall()]
        user_migrations = [
            ("name", "TEXT NOT NULL DEFAULT 'User'"),
            ("email", "TEXT NOT NULL DEFAULT ''"),
            ("password_hash", "TEXT NOT NULL DEFAULT ''"),
            ("avatar", "TEXT DEFAULT 'avatar-1'"),
            ("created_at", "TEXT NOT NULL DEFAULT ''"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
            ("settings_json", "TEXT DEFAULT '{}'")
        ]
        for col_name, col_def in user_migrations:
            if col_name not in existing_user_cols:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")

        # Seed optional demo user into SQLite if not present (using secure hash)
        demo_user = conn.execute("SELECT id FROM users WHERE LOWER(email) = 'test@example.com'").fetchone()
        if not demo_user:
            import uuid
            from werkzeug.security import generate_password_hash
            demo_id = str(uuid.uuid4())
            demo_hash = generate_password_hash("Test@12345")
            now_iso = datetime.utcnow().isoformat()
            demo_settings = json.dumps({
                "theme": "dark",
                "ai_model": "gemini-3.8-flash",
                "temperature": 0.7,
                "system_instruction": "You are a helpful, expert AI coding and learning assistant."
            })
            conn.execute("""
                INSERT INTO users (id, name, email, password_hash, avatar, created_at, updated_at, settings_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (demo_id, "Demo User", "test@example.com", demo_hash, "avatar-1", now_iso, now_iso, demo_settings))

        # Projects table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                color TEXT DEFAULT '#6366f1',
                system_instructions TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Chats table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                project_id TEXT DEFAULT NULL,
                title TEXT NOT NULL,
                is_pinned INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            );
        """)

        # Messages table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
                content TEXT NOT NULL,
                attachments_json TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            );
        """)

        # Library Files table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                project_id TEXT DEFAULT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                parsed_text TEXT DEFAULT '',
                summary TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            );
        """)

        # Indexes for fast querying & search
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_id, updated_at DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chats_pinned ON chats(user_id, is_pinned);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, created_at ASC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_files_user ON files(user_id, created_at DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id, updated_at DESC);")

    conn.close()
    return True


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DATABASE_PATH)
