from fastapi import APIRouter, Depends, Query
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.industry import Industry
from src.core.auth import require_api_key
from src.database import get_async_session
from src.schemas.industry import CreateIndustry, IndustryResponse
from src.logs.error_handler import handle_exceptions

router = APIRouter(prefix="/industry", tags=['Индустрия'])

class OrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"

@router.post("/", response_model=IndustryResponse)
async def create_industry(
        payload: CreateIndustry,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        industry = (await session.execute(select(Industry.name).where(Industry.name == payload.name.strip()))).scalar_one_or_none()
        if industry:
            return {'data': {}, 'status': 400, 'message': f"Industry already exists.", 'error': None}
        
        item = Industry(name = payload.name.strip())
        session.add(item)
        await session.commit()
        return {'data': {'id': item.id, 'name': item.name}, 'status': 200, 'message': "Industry saved successfully.", 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "The industry has not been created.")

@router.get("/", response_model=IndustryResponse)
async def get_industry(
        order: OrderEnum = Query(
        default=OrderEnum.asc,
        description="Порядок сортировки: asc (по возрастание) или desc (по убывание)"
    ),
        session: AsyncSession = Depends(get_async_session)
    ):
    try:
        stmt = select(Industry)
        if order == OrderEnum.desc:
            stmt = stmt.order_by(Industry.id.desc())
        else:
            stmt = stmt.order_by(Industry.id)

        industry = (
            await session.execute(stmt)
        ).scalars().all()

        return {'data': [{'id': item.id, 'name': item.name} for item in industry], 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return await handle_exceptions(session, [], err, "The industry has not been responsed.")

@router.put("/{industry_id}", response_model=IndustryResponse)
async def update_industry(
        industry_id: int,
        payload: CreateIndustry,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        item = (
            await session.execute(select(Industry).where(Industry.id == industry_id))
        ).scalar_one_or_none()

        if not item:
            return {'data': {}, 'status': 404, 'message': "Industry not found.", 'error': None}

        duplicate = (
            await session.execute(
                select(Industry)
                .where(Industry.name == payload.name.strip())
                .where(Industry.id != industry_id)
            )
        ).scalar_one_or_none()

        if duplicate:
            return {'data': {}, 'status': 400, 'message': "Industry name already exists.", 'error': None}
        
        item = (await session.execute(select(Industry).where(Industry.id == industry_id))).scalar_one_or_none()
        item.name = payload.name.strip()

        await session.commit()
        await session.refresh(item)
        return {'data': {'id': item.id, 'name': item.name}, 'status': 200, 'message': "Industry updated successfully.", 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "The industry has not been updated.")
    
@router.delete("/{industry_id}", response_model=IndustryResponse)
async def create_industry(
        industry_id: int,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        item = (
            await session.execute(select(Industry).where(Industry.id == industry_id))
        ).scalar_one_or_none()

        if not item:
            return {'data': {}, 'status': 404, 'message': "Industry not found.", 'error': None}
        
        await session.delete(item)
        await session.commit()

        await session.commit()
        return {'data': {}, 'status': 200, 'message': "Industry deleted successfully.", 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "The industry has not been deleted.")