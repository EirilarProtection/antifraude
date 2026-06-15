import sqlite3

DB = "database.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        ip_address TEXT,
        city TEXT,
        country TEXT,
        browser TEXT,
        account_status TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_logins():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM logins")
    rows = c.fetchall()

    conn.close()
    return [dict(r) for r in rows]


def get_user_by_id(user_id):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM logins WHERE id=?", (user_id,))
    row = c.fetchone()

    conn.close()
    return dict(row) if row else {}


def update_status(user_id, status):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "UPDATE logins SET account_status=? WHERE id=?",
        (status, user_id)
    )

    conn.commit()
    conn.close()
