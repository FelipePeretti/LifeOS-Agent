import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "lifeos.db")


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    with get_connection() as conn:
        cursor = conn.cursor()

        # ===== USERS =====
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                whatsapp_number TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ===== TRANSACTIONS =====
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(whatsapp_number)
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);"
        )

        # ===== BUDGET_GOALS =====
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                monthly_limit REAL NOT NULL,
                UNIQUE(user_id, category),
                FOREIGN KEY (user_id) REFERENCES users(whatsapp_number)
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_budget_goals_user ON budget_goals(user_id);"
        )

        # ===== CALENDAR_LOGS =====
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_summary TEXT,
                event_date TEXT,
                google_event_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(whatsapp_number)
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_calendar_logs_user ON calendar_logs(user_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_calendar_logs_date ON calendar_logs(event_date);"
        )

    print(f"✅ Database inicializado em: {DB_PATH}")
    return {"status": "ok", "path": DB_PATH}


if __name__ == "__main__":
    init_database()
