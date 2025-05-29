import sqlite3

def safe_add_columns():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Додаємо поле created_at, якщо його ще немає
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT;")
        print("✅ Поле 'created_at' додано.")
    except sqlite3.OperationalError:
        print("⚠️ Поле 'created_at' вже існує.")

    # Додаємо поле last_seen, якщо його ще немає
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_seen TEXT;")
        print("✅ Поле 'last_seen' додано.")
    except sqlite3.OperationalError:
        print("⚠️ Поле 'last_seen' вже існує.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    safe_add_columns()