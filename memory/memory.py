from memory.database import get_connection


def save_memory(key, value):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO memories(key, value)
    VALUES(?,?)
    """, (key, value))

    conn.commit()
    conn.close()


def get_memory(key):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM memories WHERE key=?",
        (key,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None