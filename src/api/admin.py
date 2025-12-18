from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_async_session
from src.schemas.users import AdminAuth
from src.logs.error_handler import handle_exceptions
from src.core.security import verify_password
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="src/core/.env")

router = APIRouter(prefix="/admin/auth", tags=['Admin-panel'])

@router.post("/login")
async def auth_admin(
        payload: AdminAuth,
        session: AsyncSession = Depends(get_async_session)
    ):
    try:
        if not payload.username or not payload.password:
            return {'data': {}, 'status': 400, 'message': 'The fields username and password cannot be empty.', 'error': None}
        
        if payload.username != os.getenv('ADMIN_USERNAME'):
            return {'data': {}, 'status': 401, 'message': 'Wrong username.', 'error': None}
        
        if not verify_password(payload.password, os.getenv('ADMIN_PASSWORD')):
            return {'data': {}, 'status': 401, 'message': 'Wrong password.', 'error': None}
        
        return {'data': {'api_key': str(os.getenv("API_KEY"))}, 'status': 200, 'message': 'Login successful.', 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Admin auth")