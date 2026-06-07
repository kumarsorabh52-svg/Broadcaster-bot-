import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS groups (
    chat_id INTEGER PRIMARY KEY,
    title TEXT
)
""")

conn.commit()

def save_user(user_id, username):
    cur.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?)",
        (user_id, username)
    )
    conn.commit()

def save_group(chat_id, title):
    cur.execute(
        "INSERT OR IGNORE INTO groups VALUES (?, ?)",
        (chat_id, title)
    )
    conn.commit()

def get_groups():
    cur.execute("SELECT chat_id,title FROM groups")
    return cur.fetchall()
