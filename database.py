import sqlite3
import bcrypt
import os
from contextlib import contextmanager

DB_NAME = "chat.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                username TEXT NOT NULL
            )
        """)
        
        # Ensure the users table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
    print("Database initialized.")

def save_user(username, password):
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        with get_db_connection() as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_user(username):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()

def check_user(username, password):
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

    if result:
        stored_hash = result['password']
        
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
            
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
    return False

def get_messages():
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT content, username, timestamp FROM messages ORDER BY timestamp ASC")
        # Convert rows to dicts
        messages = [{"content": row['content'], "username": row['username'], "timestamp": row['timestamp']} for row in cursor.fetchall()]
    return messages

def save_message(content, username):
    with get_db_connection() as conn:
        conn.execute("INSERT INTO messages (content, username) VALUES (?, ?)", (content, username))
        conn.commit()

def clear_messages():
    with get_db_connection() as conn:
        conn.execute("DELETE FROM messages")
        conn.execute("INSERT INTO messages (content, username) VALUES (?, ?)", ("Hello, World!", "System"))
        conn.commit()

def list_users():
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT username FROM users")
        users = [row['username'] for row in cursor.fetchall()]
    return users

def update_user_password(username, new_password):
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    with get_db_connection() as conn:
        conn.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()

if __name__ == "__main__":
    init_db()
