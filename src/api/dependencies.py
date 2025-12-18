from typing import Annotated

from fastapi import Depends, status, HTTPException
from src.core.jwt import verify_access_token
from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.users import Users

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

