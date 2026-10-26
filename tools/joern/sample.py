import sqlite3

def register_user(name, email):
    conn = sqlite3.connect("app.db")
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if row:
        print("already registered")
        return row[0]
    conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    return None
