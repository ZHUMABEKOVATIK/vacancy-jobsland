from src.logs.logger_config import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

async def handle_exceptions(session: AsyncSession, data, err: Exception, context: str = ""):
    await session.rollback()

    if isinstance(err, SQLAlchemyError):
        logger.error(f"[DB ERROR] {context}: {err}")
        return {
            'data': data,
            'status': 500,
            'message': None,
            'error': 'Internal database error.'
        }

    logger.error(f"[ERROR] {context}: {err}")
    return {
        'data': data,
        'status': 500,
        'message': None,
        'error': 'Internal server error.'
    }