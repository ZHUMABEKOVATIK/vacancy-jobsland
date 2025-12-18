from fastapi import APIRouter, Depends, HTTPException, status, Form

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from src.models.locations import Country, Region
from src.database import get_async_session
from src.logs.error_handler import handle_exceptions

router = APIRouter(prefix="/countries", tags=['Countries and Regions'])

@router.get("/", description="Get Countries list")
async def get_countries_list(session: AsyncSession = Depends(get_async_session)):
    try:
        countries = await session.execute(
            select(Country)
            .where(Country.is_active.is_(True))
            .order_by(Country.id.asc())
        )
        items = countries.scalars().all()
        return {
            'data': [
                { 
                    'id': item.id, 
                    'name': item.name
                } 
                for item in items
            ]
        }
    except Exception as err:
        print(f"Server error: {err}")
        raise HTTPException(500, detail="Error")

@router.get("/{country_id}", description="Get regions with country id")
async def get_countries_list(country_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        country = (await session.execute(
            select(Country)
            .where(Country.id == country_id)
        )).scalar_one_or_none()

        if not country:
            return {'data': {}, 'status': 404, 'message': 'Country not found.', 'error': None }
        
        regions = (await session.execute(
            select(Region)
            .where(Region.country_id == country.id)
            .order_by(Region.id)
        )).scalars().all()

        return {'data': {
                'id': country.id,
                'name': country.name,
                'regions': [
                    {
                        'id': i.id,
                        'name': i.name
                    }
                    for i in (regions or []) if i.is_active
                ]
            }, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Get regions error!")

@router.get("/{country_id}", description="Get regions with country id")
async def get_countries_list(country_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        country = (await session.execute(
            select(Country)
            .where(Country.id == country_id)
        )).scalar_one_or_none()

        if not country:
            return {'data': {}, 'status': 404, 'message': 'Country not found.', 'error': None }
        
        return {
            'data' : {
                'id': country.id, 
                'name': country.name, 
                'regions': [
                    {'id': item.id, 'name': item.name}
                    for item in country.regions if item.is_active
                ]
            },
            'status': 200, 'message': None, 'error': None
            }
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Get regions error!")