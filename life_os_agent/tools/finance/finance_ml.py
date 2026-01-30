from __future__ import annotations

import os
from typing import Any, Dict, Optional

import joblib
import numpy as np

_MODEL = None
_MODEL_PATH = None


def _load_model(model_path: str):
    global _MODEL, _MODEL_PATH
    if _MODEL is None or _MODEL_PATH != model_path:
        _MODEL = joblib.load(model_path)
        _MODEL_PATH = model_path
    return _MODEL


def predict_category_ptbr(
    text: str, model_path: Optional[str] = None
) -> Dict[str, Any]:
    if not text:
        return {"status": "error", "error": "empty_text"}
    if model_path is None:
        model_path = os.getenv(
            "LIFEOS_MODEL_PATH", "models/expense_clf_tfidf_nb_ptbr.joblib"
        )
    model = _load_model(model_path)
    print(f"DEBUG ML Input: '{text}'")
    proba = model.predict_proba([text])[0]
    print("PROBABILIDADES: ", proba)
    idx = int(np.argmax(proba))
    print("CATEGORIA: ", str(model.classes_[idx]))
    return {
        "status": "success",
        "category": str(model.classes_[idx]),
        "confidence": float(proba[idx]),
    }
