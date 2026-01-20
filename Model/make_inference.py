import joblib
import numpy as np

import re
from decimal import Decimal, InvalidOperation

_amount_pattern = re.compile(
    r"""(?ix)
    (?:r\$\s*)?                # opcional "R$"
    (?:
        \d{1,3}(?:\.\d{3})+    # 1.234 ou 12.345.678 (com milhar)
        |\d+                   # ou 1234
    )
    (?:[,\.\s]\d{2})?          # opcional centavos ,99 ou .99
    """
)

def _to_decimal_brl(s: str) -> Decimal | None:
    s = s.strip().lower().replace("r$", "").strip()
    s = s.replace(" ", "")

    # caso clássico BR: 1.450,00
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    # caso só vírgula: 32,90
    elif "," in s:
        s = s.replace(",", ".")
    # caso só ponto: 32.90 (já ok)
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def extract_amount_brl(text: str) -> Decimal | None:
    if not text:
        return None

    matches = _amount_pattern.findall(text)
    if not matches:
        return None

    # normalmente o valor do gasto está no final → pega o último que for válido
    for m in reversed(matches):
        val = _to_decimal_brl(m)
        if val is not None:
            return val
    return None



model = joblib.load("expense_clf_tfidf_nb_ptbr.joblib")

def predict_cat(text, thr=0.35):
    proba = model.predict_proba([text])[0]
    idx = int(np.argmax(proba))
    cat = model.classes_[idx]
    conf = float(proba[idx])
    if conf < thr:
        return "Outros", conf
    return cat, conf

def predict_with_amount(text: str, thr=0.35):
    amount = extract_amount_brl(text)
    proba = model.predict_proba([text])[0]
    idx = int(np.argmax(proba))
    cat = model.classes_[idx]
    conf = float(proba[idx])
    if conf < thr:
        cat = "Outros"
    return {
        "text": text,
        "category": cat,
        "confidence": conf,
        "amount_brl": str(amount) if amount is not None else None
    }

print(predict_with_amount("Fui de Uber para o trabalho R$ 32,90"))
print(predict_with_amount("Paguei aluguel do apê R$ 1.450,00"))
print(predict_with_amount("Renovação Netflix R$ 39,90"))
print(predict_with_amount("Compra no supermercado R$ 150,00"))
print(predict_with_amount("Jantar fora com amigos R$ 250,00"))
print(predict_with_amount("Compra de roupas na Zara R$ 350,00"))
print(predict_with_amount("Passeio no parque R$ 50,00"))
print(predict_with_amount("fui na cafeteria 50"))

