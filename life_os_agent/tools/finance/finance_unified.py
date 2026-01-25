from typing import Dict, Any
from life_os_agent.tools.finance.transaction_pipeline import make_transaction_payload, apply_confirmation
from life_os_agent.tools.finance.pending_store import set_pending_transaction, get_pending_transaction, clear_pending_transaction, has_pending_transaction

def process_finance_input(user_text: str, user_id: str = "default") -> Dict[str, Any]:
    """
    Processa entrada financeira de forma unificada.
    Decide automaticamente se é uma nova transação ou confirmação de pendência.
    Retorna JSON indicando qual ação o Orquestrador deve tomar (SALVAR ou CONFIRMAR).
    """
    
    # 0. Safety Check
    if not user_text or len(user_text.strip()) < 2:
        return {"status": "ignored", "message": "Input too short coverage"}

    # 1. Checa se existe pendência
    pending_check = has_pending_transaction()
    if pending_check.get("has_pending"):
        pending_payload = get_pending_transaction().get("pending")
        
        # Tenta aplicar confirmação
        result = apply_confirmation(user_text, pending_payload)
        
        if result["status"] == "ok":
            # Confirmado!
            # NÃO salva aqui. Retorna instrução para o Orquestrador chamar o DatabaseAgent.
            clear_pending_transaction()
            result["action"] = "save_transaction" # Sinal para o Orchestrator
            return result
            
        elif result["status"] == "cancelled":
            clear_pending_transaction()
            return result
        else: 
             return result

    # 2. Nova transação
    result = make_transaction_payload(user_text)
    
    if result["status"] == "ok":
        # Confiança alta
        result["action"] = "save_transaction" # Sinal para o Orchestrator
        return result
        
    elif result["status"] == "need_confirmation":
        set_pending_transaction(result["transaction_payload"])
        return result
        
    return result
