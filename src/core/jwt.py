from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY_ACCESS = os.getenv('SECRET_KEY_ACCESS')
SECRET_KEY_REFRESH = os.getenv('SECRET_KEY_REFRESH')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))

def create_token(data: dict, expires_delta: timedelta, secret_key: str, token_type: str) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": now,
        "token_type": token_type
    })
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------------------------------------------------------------------------------------------------------------------

async def create_access_token(data: dict) -> str:
    return create_token(
        data=data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=SECRET_KEY_ACCESS,
        token_type="access"
    )

async def create_refresh_token(data: dict) -> str:
    return create_token(
        data=data,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        secret_key=SECRET_KEY_REFRESH,
        token_type="refresh"
    )

# ---------------------------------------------------------------------------------------------------------------------------
async def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY_ACCESS, algorithms=[ALGORITHM])
        if payload.get("token_type") != "access":
            return None
        return payload
    except (JWTError, ExpiredSignatureError):
        return None

async def verify_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY_REFRESH, algorithms=[ALGORITHM])
        if payload.get("token_type") != "refresh":
            return None
        return payload
    except (JWTError, ExpiredSignatureError):
        return None