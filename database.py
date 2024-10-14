# database.py
import sqlite3

DB_PATH = 'chat_server.db'

# Initialize the database with a 'messages' table
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Store a new message in the database
def store_message(nickname, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (nickname, content) VALUES (?, ?)', (nickname, content))
    conn.commit()
    conn.close()

# Retrieve all messages from the database
def get_messages():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT nickname, content FROM messages')
    messages = cursor.fetchall()
    conn.close()
    return messages

