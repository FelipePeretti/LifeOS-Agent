from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext

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
    "budget_status": (
        "📊 *Status do Orçamento - {category}*\n\n"
        "💵 Meta: R$ {limit}\n"
        "💸 Gasto: R$ {spent} ({percent}%)\n"
        "💰 Restante: R$ {remaining}\n\n"
        "{alert_message}"
    ),
    "goal_set": (
        "🎯 *Meta Definida com Sucesso!*\n\n"
        "📂 Categoria: *{category}*\n"
        "💰 Limite mensal: R$ {limit}\n\n"
        "Vou te avisar quando estiver perto do limite."
    ),
    "welcome": (
        "👋 *Olá {name}!* Sou o LifeOS.\n\n"
        "Estou aqui para organizar sua vida financeira e pessoal.\n"
        "Você pode me dizer coisas como:\n"
        '- "Gastei 50 no almoço"\n'
        '- "Quanto gastei de mercado?"\n'
        '- "Marque uma reunião amanhã às 15h"'
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
    template_name: str, data: Dict[str, Any], tool_context: ToolContext
) -> Dict[str, Any]:
    try:
        message_body = render_template(template_name, **data)
        return send_whatsapp_response(message_body, tool_context)
    except Exception as e:
        return {"status": "error", "message": str(e)}
