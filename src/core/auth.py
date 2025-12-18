from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import Users
from src.database import get_async_session
from src.core.jwt import verify_access_token

from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/telegram/webapp/auth")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_async_session)) -> Users:
    payload = await verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    telegram_id = payload.get("telegram_id")
    if user_id is None or telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
        telegram_id = int(telegram_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad token payload types",
            headers={"WWW-Authenticate": "Bearer"},
        )

    res = await session.execute(
        select(Users)
        .where(
            and_(
                Users.id == int(user_id),
                Users.telegram_id == int(telegram_id)
            )
        )
    )
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def require_api_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing API Key"
        )
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return True

