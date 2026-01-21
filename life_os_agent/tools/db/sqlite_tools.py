import sqlite3
from typing import Any, Dict, List, Optional
import os   

DB_PATH = "lifeos.sqlite3"


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(os.getenv("DB_PATH", DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    # Importante para FK funcionar no SQLite
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def init_db() -> Dict[str, Any]:
    with _conn() as con:
        # USERS
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              whatsapp_number TEXT PRIMARY KEY,
              name TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # TRANSACTIONS
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              description TEXT,
              amount REAL NOT NULL,
              category TEXT,
              type TEXT NOT NULL,          -- expense|income
              date TIMESTAMP NOT NULL,     -- ISO string OK

              FOREIGN KEY (user_id) REFERENCES users(whatsapp_number)
            );
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_cat  ON transactions(user_id, category);")

        # BUDGET_GOALS
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS budget_goals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              category TEXT NOT NULL,
              monthly_limit REAL NOT NULL,

              FOREIGN KEY (user_id) REFERENCES users(whatsapp_number)
            );
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_budget_goals_user_cat ON budget_goals(user_id, category);")

        # CALENDAR_LOGS
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              event_summary TEXT,
              event_date TEXT,
              google_event_id TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

              FOREIGN KEY (user_id) REFERENCES users(whatsapp_number)
            );
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_calendar_logs_user_date ON calendar_logs(user_id, event_date);")

    return {"status": "ok"}


def upsert_user(whatsapp_number: str, name: Optional[str] = None) -> Dict[str, Any]:
    if not whatsapp_number:
        return {"status": "error", "error": "missing_whatsapp_number"}

    with _conn() as con:
        # se já existir, mantém; se não existir, cria
        con.execute(
            """
            INSERT OR IGNORE INTO users (whatsapp_number, name)
            VALUES (?, ?)
            """,
            (whatsapp_number, name),
        )
        # se name vier e usuário já existir sem name, atualiza
        if name:
            con.execute(
                """
                UPDATE users SET name = COALESCE(name, ?)
                WHERE whatsapp_number = ?
                """,
                (name, whatsapp_number),
            )
    return {"status": "ok"}


def save_transaction(transaction_payload: Dict[str, Any], user_id: str = "default") -> Dict[str, Any]:
    """
    Espera payload no formato:
    {
      amount, category, currency, description, direction, raw_text, ts_iso, confidence
    }

    Mapeia:
    - transactions.type  <- direction
    - transactions.date  <- ts_iso
    """
    if not isinstance(transaction_payload, dict):
        return {"status": "error", "error": "invalid_payload"}

    # cria usuário se não existir (FK)
    upsert_user(user_id)

    amount = transaction_payload.get("amount")
    direction = transaction_payload.get("direction")
    ts_iso = transaction_payload.get("ts_iso")

    if amount is None:
        return {"status": "error", "error": "missing_field:amount"}
    if not direction:
        return {"status": "error", "error": "missing_field:direction"}
    if not ts_iso:
        return {"status": "error", "error": "missing_field:ts_iso"}

    description = transaction_payload.get("description")
    category = transaction_payload.get("category")

    with _conn() as con:
        cur = con.execute(
            """
            INSERT INTO transactions (user_id, description, amount, category, type, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, description, float(amount), category, str(direction), str(ts_iso)),
        )
        new_id = cur.lastrowid

    return {"status": "ok", "inserted_id": new_id}


def get_transactions(
    user_id: str,
    limit: int = 10,
    type: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    if not user_id:
        return {"status": "error", "error": "missing_user_id"}

    q = """
    SELECT id, user_id, description, amount, category, type, date
    FROM transactions
    WHERE user_id = ?
    """
    params: List[Any] = [user_id]

    if type:
        q += " AND type = ?"
        params.append(type)

    if category:
        q += " AND category = ?"
        params.append(category)

    q += " ORDER BY date DESC LIMIT ?"
    params.append(int(limit))

    with _conn() as con:
        rows = con.execute(q, params).fetchall()

    items = [dict(r) for r in rows]
    return {"status": "ok", "transactions": items}


# Extras (opcional agora, mas já alinhado ao seu diagrama)

def set_budget_goal(user_id: str, category: str, monthly_limit: float) -> Dict[str, Any]:
    upsert_user(user_id)
    with _conn() as con:
        # estratégia simples: remove e recria para (user_id, category)
        con.execute("DELETE FROM budget_goals WHERE user_id = ? AND category = ?", (user_id, category))
        cur = con.execute(
            """
            INSERT INTO budget_goals (user_id, category, monthly_limit)
            VALUES (?, ?, ?)
            """,
            (user_id, category, float(monthly_limit)),
        )
        return {"status": "ok", "id": cur.lastrowid}


def log_calendar_event(
    user_id: str,
    event_summary: str,
    event_date: str,
    google_event_id: Optional[str] = None,
) -> Dict[str, Any]:
    upsert_user(user_id)
    with _conn() as con:
        cur = con.execute(
            """
            INSERT INTO calendar_logs (user_id, event_summary, event_date, google_event_id)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, event_summary, event_date, google_event_id),
        )
        return {"status": "ok", "id": cur.lastrowid}
