# shared/callbacks.py
from aiogram.filters.callback_data import CallbackData
from typing import Literal
import hmac, hashlib, base64, time

# Короткие коды, чтобы влезать в лимит 64 байта
VacType = Literal["job", "grant", "intern", "otits"]
Action = Literal["accept", "reject"]

SECRET = b"super-secret-between-services"  # хранить в .env

class ModAction(CallbackData, prefix="mod"):
    action: Action
    vacancy_type: VacType
    vacancy_id: int
    token: str

# def make_token(vacancy_type: str, vacancy_id: int, action: str, ttl_sec: int = 3600) -> str:
#     ts = int(time.time()) // ttl_sec  # скользящее окно
#     msg = f"{vacancy_type}:{vacancy_id}:{action}:{ts}".encode()
#     sig = hmac.new(SECRET, msg, hashlib.sha256).digest()
#     # делаем токен короче (12 байт) и url-safe
#     return base64.urlsafe_b64encode(sig[:12]).decode().rstrip("=")

# def verify_token(vacancy_type: str, vacancy_id: int, action: str, token: str, ttl_sec: int = 3600) -> bool:
#     ts = int(time.time()) // ttl_sec
#     for delta in (0, -1, 1):  # допускаем соседние окна, чтобы не было гонок
#         msg = f"{vacancy_type}:{vacancy_id}:{action}:{ts+delta}".encode()
#         sig = hmac.new(SECRET, msg, hashlib.sha256).digest()
#         good = base64.urlsafe_b64encode(sig[:12]).decode().rstrip("=")
#         if hmac.compare_digest(good, token):
#             return True
#     return False
