from typing import Any, Dict, Optional

from life_os_agent.database.crud import get_or_create_user


def get_or_create_user_tool(
    whatsapp_number: str, name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verifica se um usuário existe no banco de dados. Se não existir, cria um novo.
    Atualiza automaticamente a última interação do usuário.

    Args:
        whatsapp_number: Número do WhatsApp do usuário (ex: "5511999999999")
        name: Nome do usuário (opcional, usado apenas na criação)

    Returns:
        Dicionário com:
        - whatsapp_number: Número do usuário
        - name: Nome do usuário
        - created_at: Data de criação
        - last_interaction: Última interação
        - is_new_user: True se o usuário acabou de ser criado
        - is_first_interaction_today: True se é a primeira interação do dia
    """
    return get_or_create_user(whatsapp_number, name)
