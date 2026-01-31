from typing import Any, Dict

from life_os_agent.tools.whatsapp.send_response import send_whatsapp_response

MESSAGE_TEMPLATES = {
    "daily_summary": (
        "🌞 *Bom dia! Aqui está seu resumo:*\n\n"
        "💰 *Saldo Atual:* R$ {balance}\n"
        "📅 *Hoje:* {events}\n\n"
        "Deseja ver detalhes de alguma categoria?"
    ),
    "alert_spending": (
        "⚠️ *Alerta de Gastos*\n\n"
        "A categoria *{category}* atingiu *{percent}%* da sua meta mensal.\n"
        "Gasto atual: R$ {spent} / Meta: R$ {limit}\n\n"
        "Recomendo cautela nos próximos dias!"
    ),
    "welcome": (
        "👋 *Olá {name}!* Sou o LifeOS.\n\n"
        "Estou aqui para organizar sua vida financeira e pessoal.\n"
        "Você pode me dizer coisas como:\n"
        '- "Gastei 50 no almoço"\n'
        '- "Qual meu saldo?"\n'
        '- "Me lembre de beber água"'
    ),
    "transaction_confirmed": (
        "✅ *Registrado!*\n\nR$ {amount} em *{category}*\n{budget_info}"
    ),
}


def render_template(template_name: str, **kwargs) -> str:
    template = MESSAGE_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Template '{template_name}' not found.")

    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Error rendering template: Missing data field {e}"


def send_template_message_tool(
    phone_number: str, template_name: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        message_body = render_template(template_name, **data)
        return send_whatsapp_response(phone_number, message_body)
    except Exception as e:
        return {"status": "error", "message": str(e)}
