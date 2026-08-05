import sqlite3

DB_NAME = "memory/memory.db"


def remember(key, value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO memories(key, value)
        VALUES (?, ?)
    """, (key.lower(), value))

    conn.commit()
    conn.close()

    return f"I'll remember that your {key} is {value}."


def recall(key):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT value
        FROM memories
        WHERE key=?
    """, (key.lower(),))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None