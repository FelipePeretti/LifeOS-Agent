"""
Parser de datas relativas para o Calendar Agent.

Este módulo converte expressões de data/hora em linguagem natural
para o formato ISO 8601 que o Google Calendar espera.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re


# Mapeamento de dias da semana em português
DIAS_SEMANA = {
    "segunda": 0,
    "segunda-feira": 0,
    "terça": 1,
    "terca": 1,
    "terça-feira": 1,
    "terca-feira": 1,
    "quarta": 2,
    "quarta-feira": 2,
    "quinta": 3,
    "quinta-feira": 3,
    "sexta": 4,
    "sexta-feira": 4,
    "sábado": 5,
    "sabado": 5,
    "domingo": 6,
}

# Expressões de data relativa
EXPRESSOES_RELATIVAS = {
    "hoje": 0,
    "amanhã": 1,
    "amanha": 1,
    "depois de amanhã": 2,
    "depois de amanha": 2,
    "ontem": -1,
    "anteontem": -2,
}


def _normalizar_texto(texto: str) -> str:
    """Normaliza o texto para facilitar o parsing."""
    return texto.lower().strip()


def _get_proximo_dia_semana(dia_semana: int, referencia: datetime = None) -> datetime:
    """
    Retorna a data do próximo dia da semana especificado.
    
    Se hoje for o dia especificado, retorna hoje.
    Caso contrário, retorna o próximo dia da semana.
    """
    if referencia is None:
        referencia = datetime.now()
    
    dias_ate_proximo = (dia_semana - referencia.weekday()) % 7
    # Se for 0, significa que é hoje - retorna hoje
    if dias_ate_proximo == 0:
        return referencia
    return referencia + timedelta(days=dias_ate_proximo)


def _get_ultimo_dia_semana(dia_semana: int, referencia: datetime = None) -> datetime:
    """
    Retorna a data do último dia da semana especificado (passado).
    """
    if referencia is None:
        referencia = datetime.now()
    
    dias_desde_ultimo = (referencia.weekday() - dia_semana) % 7
    if dias_desde_ultimo == 0:
        dias_desde_ultimo = 7  # Se for hoje, pega o da semana passada
    return referencia - timedelta(days=dias_desde_ultimo)


def parse_data_relativa(texto: str, referencia: datetime = None) -> Optional[datetime]:
    """
    Converte uma expressão de data relativa em datetime.
    
    Args:
        texto: Expressão de data (ex: "hoje", "amanhã", "sexta", "última segunda")
        referencia: Data de referência (default: agora)
    
    Returns:
        datetime ou None se não conseguir parsear
    
    Exemplos:
        - "hoje" -> data atual
        - "amanhã" -> data atual + 1 dia
        - "sexta" -> próxima sexta-feira (ou hoje se for sexta)
        - "última sexta" -> sexta-feira passada
        - "próxima segunda" -> próxima segunda-feira
    """
    if referencia is None:
        referencia = datetime.now()
    
    texto_norm = _normalizar_texto(texto)
    
    # Verifica expressões relativas simples
    for expr, dias in EXPRESSOES_RELATIVAS.items():
        if expr in texto_norm:
            return referencia + timedelta(days=dias)
    
    # Verifica se menciona "última/ultimo" ou "passada/passado"
    is_passado = any(p in texto_norm for p in ["última", "ultima", "último", "ultimo", "passada", "passado"])
    
    # Verifica se menciona "próxima/próximo"
    is_proximo = any(p in texto_norm for p in ["próxima", "proxima", "próximo", "proximo"])
    
    # Procura por dia da semana
    for dia_nome, dia_num in DIAS_SEMANA.items():
        if dia_nome in texto_norm:
            if is_passado:
                return _get_ultimo_dia_semana(dia_num, referencia)
            else:
                resultado = _get_proximo_dia_semana(dia_num, referencia)
                # Se pediu explicitamente "próxima" e hoje é o dia, vai pra semana que vem
                if is_proximo and resultado.date() == referencia.date():
                    resultado = resultado + timedelta(days=7)
                return resultado
    
    return None


def parse_horario(texto: str) -> Optional[Tuple[int, int]]:
    """
    Extrai horário de um texto.
    
    Args:
        texto: Texto contendo horário (ex: "18h", "14:30", "às 9")
    
    Returns:
        Tupla (hora, minuto) ou None
    
    Exemplos:
        - "18h" -> (18, 0)
        - "14h30" -> (14, 30)
        - "9:45" -> (9, 45)
        - "às 10" -> (10, 0)
    """
    texto_norm = _normalizar_texto(texto)
    
    # Padrão: 14h30, 18h, 9h
    match = re.search(r'(\d{1,2})h(\d{2})?', texto_norm)
    if match:
        hora = int(match.group(1))
        minuto = int(match.group(2)) if match.group(2) else 0
        if 0 <= hora <= 23 and 0 <= minuto <= 59:
            return (hora, minuto)
    
    # Padrão: 14:30, 9:45
    match = re.search(r'(\d{1,2}):(\d{2})', texto_norm)
    if match:
        hora = int(match.group(1))
        minuto = int(match.group(2))
        if 0 <= hora <= 23 and 0 <= minuto <= 59:
            return (hora, minuto)
    
    # Padrão: às 18, as 9
    match = re.search(r'[àa]s?\s*(\d{1,2})(?:\s|$)', texto_norm)
    if match:
        hora = int(match.group(1))
        if 0 <= hora <= 23:
            return (hora, 0)
    
    return None


def is_dia_inteiro(texto: str) -> bool:
    """
    Verifica se o texto indica um evento de dia inteiro.
    
    Args:
        texto: Texto do evento
    
    Returns:
        True se for evento de dia inteiro
    
    Exemplos:
        - "o dia todo" -> True
        - "dia inteiro" -> True
        - "durante todo o dia" -> True
    """
    texto_norm = _normalizar_texto(texto)
    
    padroes_dia_inteiro = [
        "dia todo",
        "o dia todo",
        "dia inteiro",
        "o dia inteiro",
        "todo o dia",
        "durante todo o dia",
        "all day",
        "full day",
    ]
    
    return any(padrao in texto_norm for padrao in padroes_dia_inteiro)


def parse_datetime_completo(
    texto: str,
    referencia: datetime = None,
    duracao_padrao_horas: float = 1.0
) -> dict:
    """
    Faz o parsing completo de uma expressão de data/hora.
    
    Args:
        texto: Texto contendo data e/ou hora
        referencia: Data de referência (default: agora)
        duracao_padrao_horas: Duração padrão do evento em horas
    
    Returns:
        Dict com:
        - start_datetime: ISO 8601 do início (ou só data se all_day)
        - end_datetime: ISO 8601 do fim (ou só data se all_day)
        - all_day: True se for evento de dia inteiro
        - parsed_date: datetime da data parseada
        - parsed_time: Tupla (hora, minuto) se horário foi parseado
    
    Exemplos:
        parse_datetime_completo("hoje às 18h")
        -> {
            "start_datetime": "2026-01-31T18:00:00",
            "end_datetime": "2026-01-31T19:00:00",
            "all_day": False,
            ...
        }
        
        parse_datetime_completo("amanhã o dia todo")
        -> {
            "start_datetime": "2026-02-01",
            "end_datetime": "2026-02-01",
            "all_day": True,
            ...
        }
    """
    if referencia is None:
        referencia = datetime.now()
    
    resultado = {
        "start_datetime": None,
        "end_datetime": None,
        "all_day": False,
        "parsed_date": None,
        "parsed_time": None,
        "duracao_horas": duracao_padrao_horas,
    }
    
    # Verifica se é dia inteiro
    resultado["all_day"] = is_dia_inteiro(texto)
    
    # Tenta parsear a data
    data_parseada = parse_data_relativa(texto, referencia)
    
    # Se não conseguiu parsear data relativa, usa a data de referência
    if data_parseada is None:
        data_parseada = referencia
    
    resultado["parsed_date"] = data_parseada
    
    # Se é dia inteiro, usa apenas a data
    if resultado["all_day"]:
        data_str = data_parseada.strftime("%Y-%m-%d")
        resultado["start_datetime"] = data_str
        resultado["end_datetime"] = data_str
        return resultado
    
    # Tenta parsear o horário
    horario = parse_horario(texto)
    resultado["parsed_time"] = horario
    
    if horario:
        hora, minuto = horario
        inicio = data_parseada.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    else:
        # Se não tem horário, assume que é dia inteiro
        resultado["all_day"] = True
        data_str = data_parseada.strftime("%Y-%m-%d")
        resultado["start_datetime"] = data_str
        resultado["end_datetime"] = data_str
        return resultado
    
    # Calcula o fim baseado na duração
    fim = inicio + timedelta(hours=duracao_padrao_horas)
    
    resultado["start_datetime"] = inicio.strftime("%Y-%m-%dT%H:%M:%S")
    resultado["end_datetime"] = fim.strftime("%Y-%m-%dT%H:%M:%S")
    
    return resultado


def parse_duracao(texto: str) -> Optional[float]:
    """
    Extrai a duração de um evento do texto.
    
    Args:
        texto: Texto contendo duração
    
    Returns:
        Duração em horas ou None
    
    Exemplos:
        - "por 2 horas" -> 2.0
        - "1 hora" -> 1.0
        - "30 minutos" -> 0.5
        - "duração de 1h30" -> 1.5
    """
    texto_norm = _normalizar_texto(texto)
    
    # Padrão: "por X horas" / "X horas de duração" / "duração X horas"
    match = re.search(r'(?:por|duração\s*(?:de)?|dura)\s*(\d+(?:[.,]\d+)?)\s*horas?', texto_norm)
    if match:
        return float(match.group(1).replace(",", "."))
    
    # Padrão: X horas / X hora - mas só se NÃO for precedido por "às"
    # Procura por "X horas" no texto
    for match in re.finditer(r'(\d+(?:[.,]\d+)?)\s*horas?', texto_norm):
        # Verifica se não é precedido por "às" (que indicaria horário)
        pos = match.start()
        antes = texto_norm[:pos].rstrip()
        if not antes.endswith(('às', 'as', 'à')):
            return float(match.group(1).replace(",", "."))
    
    # Padrão: X minutos / X min
    match = re.search(r'(\d+)\s*(?:minutos?|min)(?:\s|$)', texto_norm)
    if match:
        return int(match.group(1)) / 60.0
    
    # Padrão: duração de Xh ou XhYY (duração de 1h, duração de 1h30)
    # NÃO deve capturar "às 18h" que é horário
    match = re.search(r'(?:por|duração\s*(?:de)?|dura)\s*(\d+)h(\d{1,2})?(?:\s|$)', texto_norm)
    if match:
        horas = int(match.group(1))
        minutos = int(match.group(2)) if match.group(2) else 0
        return horas + minutos / 60.0
    
    return None


def formatar_data_evento(
    texto: str,
    referencia: datetime = None,
    duracao_padrao_horas: float = 1.0
) -> dict:
    """
    Função principal para formatar data/hora de um evento.
    
    Esta é a função que deve ser usada pelo CalendarAgent para
    interpretar comandos do usuário e gerar as datas no formato correto.
    
    Args:
        texto: Comando do usuário (ex: "mercado hoje às 18h")
        referencia: Data de referência (default: agora)
        duracao_padrao_horas: Duração padrão em horas (default: 1)
    
    Returns:
        Dict com:
        - start: Data/hora de início no formato correto
        - end: Data/hora de término no formato correto  
        - all_day: Se é evento de dia inteiro
        - duracao_horas: Duração em horas
    """
    if referencia is None:
        referencia = datetime.now()
    
    # Verifica se tem duração explícita
    duracao = parse_duracao(texto)
    if duracao is not None:
        duracao_padrao_horas = duracao
    
    # Faz o parsing completo
    resultado = parse_datetime_completo(texto, referencia, duracao_padrao_horas)
    
    return {
        "start": resultado["start_datetime"],
        "end": resultado["end_datetime"],
        "all_day": resultado["all_day"],
        "duracao_horas": resultado.get("duracao_horas", duracao_padrao_horas),
    }


# Função auxiliar para testes
def get_data_atual() -> datetime:
    """Retorna a data/hora atual."""
    return datetime.now()
