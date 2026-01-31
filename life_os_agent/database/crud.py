from datetime import date, datetime
from typing import Any, Dict, List, Optional

from .setup import get_connection


def create_user(whatsapp_number: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Cria um novo usuário no banco de dados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (whatsapp_number, name, last_interaction) VALUES (?, ?, ?)",
            (whatsapp_number, name, datetime.now().isoformat()),
        )
        return {"status": "ok", "whatsapp_number": whatsapp_number, "is_new": True}


def get_user(whatsapp_number: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário pelo número do WhatsApp."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE whatsapp_number = ?", (whatsapp_number,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def check_user_exists(whatsapp_number: str) -> Dict[str, Any]:
    """Verifica se um usuário existe e se é a primeira interação do dia."""
    user = get_user(whatsapp_number)
    if user:
        last_interaction = user.get("last_interaction")
        is_first_today = True
        if last_interaction:
            try:
                last_date = datetime.fromisoformat(last_interaction).date()
                is_first_today = last_date < date.today()
            except (ValueError, TypeError):
                is_first_today = True

        return {
            "exists": True,
            "user_data": user,
            "is_first_interaction_today": is_first_today,
        }
    return {"exists": False, "user_data": None, "is_first_interaction_today": True}


def update_user_last_interaction(whatsapp_number: str) -> Dict[str, Any]:
    """Atualiza a última interação do usuário para agora."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_interaction = ? WHERE whatsapp_number = ?",
            (datetime.now().isoformat(), whatsapp_number),
        )
        return {"status": "ok", "updated": cursor.rowcount}


def update_user(whatsapp_number: str, name: str) -> Dict[str, Any]:
    """Atualiza o nome de um usuário."""
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
    """Busca um usuário ou cria se não existir. Atualiza a última interação."""
    check_result = check_user_exists(whatsapp_number)

    if check_result["exists"]:
        update_user_last_interaction(whatsapp_number)
        user_data = get_user(whatsapp_number) or {}
        result = {
            **user_data,
            "is_new_user": False,
            "is_first_interaction_today": check_result["is_first_interaction_today"],
        }
        return result

    create_user(whatsapp_number, name)
    user_data = get_user(whatsapp_number) or {}
    return {**user_data, "is_new_user": True, "is_first_interaction_today": True}


def add_transaction(
    user_id: str,
    description: str,
    amount: float,
    category: str,
    transaction_type: str,
    date: Optional[str] = None,
) -> Dict[str, Any]:
    """Adiciona uma transação financeira."""
    if transaction_type not in ("income", "expense"):
        return {"status": "error", "error": "type must be 'income' or 'expense'"}

    if not date or len(date) < 10:
        date = datetime.now().isoformat()
    elif len(date) == 10:
        date = f"{date}T{datetime.now().strftime('%H:%M:%S')}"

    create_user(user_id)

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
    """Retorna transações do usuário com filtros opcionais."""
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params: List[Any] = [user_id]

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
    """Retorna o saldo do usuário (receitas, despesas e balanço)."""
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
    """Retorna gastos agrupados por categoria."""
    query = """
        SELECT category, SUM(amount) as total
        FROM transactions 
        WHERE user_id = ? AND type = 'expense'
    """
    params: List[Any] = [user_id]

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
    """Atualiza uma transação existente."""
    updates = []
    params: List[Any] = []

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
            return {
                "status": "error",
                "error": "Transaction not found or access denied",
            }
        return {"status": "ok", "updated": cursor.rowcount}


def delete_transaction(transaction_id: int, user_id: str) -> Dict[str, Any]:
    """Deleta uma transação."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transactions WHERE id = ? AND user_id = ?",
            (transaction_id, user_id),
        )
        return {"status": "ok", "deleted": cursor.rowcount}


def set_budget_goal(
    user_id: str, category: str, monthly_limit: float
) -> Dict[str, Any]:
    """Define ou atualiza meta de orçamento para uma categoria."""
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
    """Retorna todas as metas de orçamento do usuário."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budget_goals WHERE user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_budget_status(
    user_id: str, month: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retorna o status do orçamento comparando metas com gastos reais."""
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
    """Remove uma meta de orçamento."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM budget_goals WHERE user_id = ? AND category = ?",
            (user_id, category),
        )
        return {"status": "ok", "deleted": cursor.rowcount}


def add_calendar_log(
    user_id: str,
    google_event_id: str,
    action: str,
    event_summary: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Registra uma ação de calendário (created, updated, deleted).

    Args:
        user_id: WhatsApp number do usuário
        google_event_id: ID do evento no Google Calendar
        action: Tipo de ação ('created', 'updated', 'deleted')
        event_summary: Título do evento (opcional, para referência)
    """
    if action not in ("created", "updated", "deleted"):
        return {"status": "error", "error": f"Ação inválida: {action}"}

    # Garante que o usuário existe
    create_user(user_id)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO calendar_events (user_id, google_event_id, action, event_summary)
               VALUES (?, ?, ?, ?)""",
            (user_id, google_event_id, action, event_summary),
        )
        return {"status": "ok", "id": cursor.lastrowid}


def get_calendar_events(
    user_id: str,
    limit: int = 50,
    action: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retorna log de eventos de calendário do usuário.

    Args:
        user_id: WhatsApp number do usuário
        limit: Número máximo de resultados
        action: Filtrar por tipo de ação (opcional)
    """
    query = "SELECT * FROM calendar_events WHERE user_id = ?"
    params: List[Any] = [user_id]

    if action:
        query += " AND action = ?"
        params.append(action)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_event_by_google_id(
    user_id: str,
    google_event_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Busca um evento pelo google_event_id.

    Args:
        user_id: WhatsApp number do usuário
        google_event_id: ID do evento no Google Calendar
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM calendar_events 
               WHERE user_id = ? AND google_event_id = ? 
               ORDER BY created_at DESC LIMIT 1""",
            (user_id, google_event_id),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_calendar_event_log(log_id: int, user_id: str) -> Dict[str, Any]:
    """Remove um log de evento de calendário."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM calendar_events WHERE id = ? AND user_id = ?",
            (log_id, user_id),
        )
        return {"status": "ok", "deleted": cursor.rowcount}
