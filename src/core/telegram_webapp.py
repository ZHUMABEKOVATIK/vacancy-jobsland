import hmac, hashlib, json, urllib.parse
from datetime import datetime, timezone
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

def _secret_key(bot_token: str) -> bytes:
    # ВАЖНО: для WebApp секрет — это HMAC_SHA256("WebAppData", bot_token)
    return hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

def parse_init_data(init_data_raw: str) -> dict:
    data = dict(urllib.parse.parse_qsl(init_data_raw, keep_blank_values=True))
    if "hash" not in data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing hash")
    return data

def verify_init_data(init_data_raw: str, max_age_seconds: int = 86400) -> dict:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    data = parse_init_data(init_data_raw)
    hash_from_telegram = data.pop("hash")

    # data_check_string: key=value, по алфавиту, без hash
    check_pairs = [f"{k}={v}" for k, v in sorted(data.items())]
    data_check_string = "\n".join(check_pairs)

    secret = _secret_key(BOT_TOKEN)
    calc_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    # print(calc_hash)
    # print(hash_from_telegram)
    if not hmac.compare_digest(calc_hash, hash_from_telegram):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid initData signature")

    # проверка возраста
    try:
        auth_date = int(data.get("auth_date", "0"))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad auth_date")

    if int(datetime.now(timezone.utc).timestamp()) - auth_date > max_age_seconds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="initData expired")

    # user — это JSON-строка внутри initData
    user = json.loads(data.get("user") or "null")
    if not user or "id" not in user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No user in initData")

    return {"user": user, "query": data}