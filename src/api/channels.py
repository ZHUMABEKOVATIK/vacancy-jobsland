from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from src.models.channels import Channels
from src.core.auth import require_api_key
from src.database import get_async_session
from src.schemas.channels import CreateChennel, UpdateChennel


class ResponseOut(BaseModel):
    data: dict | list
    status: int
    message: str | None
    error: str | None


router = APIRouter(prefix="/bot/channels", tags=['Каналы для размещения вакансий'])

@router.post("/", response_model=ResponseOut)
async def create_new_channel(
        payload: CreateChennel,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        stmt = (
            select(Channels)
            .where(Channels.country_id == payload.country_id)
        )
        if payload.region_id is not None:
            stmt = stmt.where(Channels.region_id == payload.region_id)
        else:
            stmt = stmt.where(Channels.region_id.is_(None))
        exiting = await session.execute(stmt)
        data = exiting.scalar_one_or_none()

        if data:
            return {'data': {}, 'status': 400, 'message': f"Channel already exists.", 'error': None}
        
        channel = Channels(
            country_id = payload.country_id,
            region_id = payload.region_id if payload.region_id is not None else None,
            channel_url = payload.channel_url
        )
        session.add(channel)
        await session.commit()
        await session.refresh(channel)
        
        return {
            'data': 
                {
                    "id": channel.id, 
                    "country": {
                        'id': channel.country.id,
                        'name': channel.country.name
                    },
                    "region": {
                        'id': channel.region.id,
                        'name': channel.region.name
                    } if channel.region_id else None,
                    "channel_url": channel.channel_url
                }, 
                'status': 201, 'message': "Channel saved successfully!", 'error': None
            }
    
    except Exception as err:
        await session.rollback()
        return {'data': {}, 'status': 500, 'message': "Server error", 'error': f"{err}"}

@router.get("/", response_model=ResponseOut)
async def get_list_channels(
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        exiting = await session.execute(select(Channels).order_by(Channels.id.desc()))
        return {
            'data': [
                {
                    'id': item.id,
                    'channel_url': item.channel_url,
                    "country": {
                        'id': item.country.id,
                        'name': item.country.name
                    },
                    "region": {
                        'id': item.region.id,
                        'name': item.region.name
                    } if item.region_id else None,
                }
                for item in exiting.scalars().all()
            ], 'status': 200, 'message': None, 'error': None
        }
    except Exception as err:
        return {'data': [], 'status': 500, 'message': "Server error", 'error': f"{err}"}

@router.put("/{item_id}", response_model=ResponseOut)
async def update_channel(
        item_id: int,
        payload: UpdateChennel,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        stmt = (
            select(Channels)
            .where(Channels.country_id == payload.country_id)
            .where(Channels.id != item_id)
        )
        if payload.region_id is not None:
            stmt = stmt.where(Channels.region_id == payload.region_id)
        else:
            stmt = stmt.where(Channels.region_id.is_(None))
        exiting = await session.execute(stmt)
        data = exiting.scalar_one_or_none()

        if data:
            return {'data': {}, 'status': 400, 'message': f"Channel already exists.", 'error': None}

        items = await session.execute(select(Channels).where(Channels.id == item_id))
        data = items.scalar_one_or_none()

        if payload.country_id is not None:
            data.country_id = payload.country_id

        data.region_id = payload.region_id

        if payload.channel_url is not None:
            data.channel_url = payload.channel_url

        await session.commit()
        await session.refresh(data)
        return {'data':{
                    "id": data.id, 
                    'channel_url': data.channel_url,
                    "country": {
                        'id': data.country.id,
                        'name': data.country.name
                    },
                    "region": {
                        'id': data.region.id,
                        'name': data.region.name
                    } if data.region_id else None,
                },
                'status': 200, 'message': f"Channel saved successfully", 'error': None
            }
    except (ValueError, SQLAlchemyError):
        await session.rollback()
        return {'data': {}, 'status': 400, 'message': f"Invalid value!", 'error': f"{err}"}
    except Exception as err:
        await session.rollback()
        return {'data': {}, 'status': 500, 'message': f"Server error!", 'error': f"{err}"}

class DeleteChannelOut(BaseModel):
    data: bool
    status: int
    message: str
    error: str | None

@router.delete("/{item_id}", response_model=DeleteChannelOut)
async def delete_channel(
        item_id: int,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        exiting = await session.execute(select(Channels).where(Channels.id == item_id))
        data = exiting.scalar_one_or_none()
        if not data:
            return {'data': False, 'status': 400, 'message': f"Chat with id={item_id} not found.", 'error': None}
        await session.delete(data)
        await session.commit()
        return {'data': True, 'status': 200, 'message': f"Chat with id={item_id} has been deleted.", 'error': None}
    except Exception as err:
        await session.rollback()
        return {'data': False, 'status': 500, 'message': f"Server error", 'error': f"{err}"}