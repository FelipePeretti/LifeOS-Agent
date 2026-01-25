from datetime import datetime
from typing import Any, Dict, List, Optional

from .setup import get_connection

# ===== USERS =====


def create_user(whatsapp_number: str, name: Optional[str] = None) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (whatsapp_number, name) VALUES (?, ?)",
            (whatsapp_number, name),
        )
        return {"status": "ok", "whatsapp_number": whatsapp_number}


def get_user(whatsapp_number: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE whatsapp_number = ?", (whatsapp_number,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def update_user(whatsapp_number: str, name: str) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = ? WHERE whatsapp_number = ?",
            (name, whatsapp_number),
        )
        return {"status": "ok", "updated": cursor.rowcount}


def get_or_create_user(
    whatsapp_number: str, name: Optional[str] = None
) -> Dict[str, Any]:
    user = get_user(whatsapp_number)
    if user:
        return user
    create_user(whatsapp_number, name)
    return get_user(whatsapp_number)


# ===== TRANSACTIONS =====


def add_transaction(
    user_id: str,
    description: str,
    amount: float,
    category: str,
    transaction_type: str,
    date: Optional[str] = None,
) -> Dict[str, Any]:
    if transaction_type not in ("income", "expense"):
        return {"status": "error", "error": "type must be 'income' or 'expense'"}

    
    # Validação e correção de data
    if not date or len(date) < 10:
        date = datetime.now().isoformat()
    # Se vier só a data (2025-01-01), adiciona hora atual pra não quebrar ordenação
    elif len(date) == 10:
        date = f"{date}T{datetime.now().strftime('%H:%M:%S')}"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO transactions (user_id, description, amount, category, type, date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, description, amount, category, transaction_type, date),
        )
        return {"status": "ok", "id": cursor.lastrowid}


def get_transactions(
    user_id: str,
    limit: int = 50,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]

    if category:
        query += " AND category = ?"
        params.append(category)
    if transaction_type:
        query += " AND type = ?"
        params.append(transaction_type)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_balance(user_id: str) -> Dict[str, float]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as expense
            FROM transactions WHERE user_id = ?
        """,
            (user_id,),
        )
        row = cursor.fetchone()
        income = row["income"]
        expense = row["expense"]
        return {"income": income, "expense": expense, "balance": income - expense}


def get_expenses_by_category(
    user_id: str, month: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = """
        SELECT category, SUM(amount) as total
        FROM transactions 
        WHERE user_id = ? AND type = 'expense'
    """
    params = [user_id]

    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)

    query += " GROUP BY category ORDER BY total DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]



def update_transaction(
    user_id: str,
    transaction_id: int,
    description: Optional[str] = None,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
) -> Dict[str, Any]:
    updates = []
    params = []

    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if transaction_type is not None:
        updates.append("type = ?")
        params.append(transaction_type)
        
    if not updates:
        return {"status": "error", "error": "No fields to update"}

    params.append(transaction_id)
    params.append(user_id)

    query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ? AND user_id = ?"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if cursor.rowcount == 0:
             return {"status": "error", "error": "Transaction not found or access denied"}
        return {"status": "ok", "updated": cursor.rowcount}


def delete_transaction(transaction_id: int, user_id: str) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transactions WHERE id = ? AND user_id = ?",
            (transaction_id, user_id),
        )
        return {"status": "ok", "deleted": cursor.rowcount}


# ===== BUDGET_GOALS =====


def set_budget_goal(
    user_id: str, category: str, monthly_limit: float
) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO budget_goals (user_id, category, monthly_limit)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = ?""",
            (user_id, category, monthly_limit, monthly_limit),
        )
        return {"status": "ok", "category": category, "monthly_limit": monthly_limit}


def get_budget_goals(user_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budget_goals WHERE user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_budget_status(
    user_id: str, month: Optional[str] = None
) -> List[Dict[str, Any]]:
    month = month or datetime.now().strftime("%Y-%m")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                bg.category,
                bg.monthly_limit,
                COALESCE(SUM(t.amount), 0) as spent
            FROM budget_goals bg
            LEFT JOIN transactions t ON 
                t.user_id = bg.user_id 
                AND t.category = bg.category 
                AND t.type = 'expense'
                AND strftime('%Y-%m', t.date) = ?
            WHERE bg.user_id = ?
            GROUP BY bg.category, bg.monthly_limit
        """,
            (month, user_id),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                {
                    "category": row["category"],
                    "monthly_limit": row["monthly_limit"],
                    "spent": row["spent"],
                    "remaining": row["monthly_limit"] - row["spent"],
                    "percentage": (row["spent"] / row["monthly_limit"] * 100)
                    if row["monthly_limit"] > 0
                    else 0,
                }
            )
        return results


def delete_budget_goal(user_id: str, category: str) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM budget_goals WHERE user_id = ? AND category = ?",
            (user_id, category),
        )
        return {"status": "ok", "deleted": cursor.rowcount}


# ===== CALENDAR_LOGS =====


def add_calendar_log(
    user_id: str,
    event_summary: str,
    event_date: str,
    google_event_id: Optional[str] = None,
) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO calendar_logs (user_id, event_summary, event_date, google_event_id)
               VALUES (?, ?, ?, ?)""",
            (user_id, event_summary, event_date, google_event_id),
        )
        return {"status": "ok", "id": cursor.lastrowid}


def get_calendar_logs(
    user_id: str,
    limit: int = 50,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM calendar_logs WHERE user_id = ?"
    params = [user_id]

    if start_date:
        query += " AND event_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND event_date <= ?"
        params.append(end_date)

    query += " ORDER BY event_date DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def delete_calendar_log(log_id: int, user_id: str) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM calendar_logs WHERE id = ? AND user_id = ?", (log_id, user_id)
        )
        return {"status": "ok", "deleted": cursor.rowcount}
