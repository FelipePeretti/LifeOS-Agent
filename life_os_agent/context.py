import threading
from typing import Optional

_lock = threading.Lock()
_current_phone: Optional[str] = None
_current_user_name: Optional[str] = None


def set_current_user(phone: str, name: Optional[str] = None) -> None:
    global _current_phone, _current_user_name
    with _lock:
        _current_phone = phone
        _current_user_name = name


def get_current_phone() -> Optional[str]:
    with _lock:
        return _current_phone


def get_current_user_name() -> Optional[str]:
    with _lock:
        return _current_user_name


def clear_current_user() -> None:
    global _current_phone, _current_user_name
    with _lock:
        _current_phone = None
        _current_user_name = None
