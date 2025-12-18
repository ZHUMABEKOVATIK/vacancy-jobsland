from fastapi import APIRouter, Depends, Form

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.locations import Country, Region
from src.schemas.locations import ActiveCountry, CreateCountry, CreateRegion
from src.database import get_async_session
from src.core.auth import require_api_key

router = APIRouter(prefix="/manage/countries", tags=['Countries for Admin'])

@router.post("/country", description="Add country")
async def add_new_country(
        payload: CreateCountry,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        country = (await session.execute(select(Country).where(Country.name == payload.name.strip()))).scalar_one_or_none()
        if country:
            return {'data': {}, 'status': 400, 'message': f"Country {payload.name.strip()} already exists.", 'error': None}

        item = Country(
            name = payload.name.strip(),
            en = payload.name.strip(),
            time_zoneutc = "UTC",
            is_active = payload.active
        )
        session.add(item)
        await session.commit()

        return {'data': {'id': item.id, 'name': item.name, 'is_active': item.is_active}, 'status': 201, 'message': "Country saved successfully! 🎉", 'error': None}
    except Exception as err:
        await session.rollback()
        return {'data': {}, 'status': 500, 'message': "Failed to save country! ❌", 'error': f"{err}"}

@router.post("/region", description="Add region")
async def add_new_region(
        payload: CreateRegion,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        country = (await session.execute(select(Country).where(Country.id == payload.country_id))).scalar_one_or_none()
        if not country:
            return {'data': {}, 'status': 404, 'message': "Country Not Found!", 'error': None}
        
        regions = (await session.execute(
            select(Region)
            .where(Region.country_id == payload.country_id)
            .where(Region.name == payload.name.strip()))
        ).scalar_one_or_none()

        if regions:
            return {'data': {}, 'status': 409, 'message': f"Region {payload.name.strip()} already exists.", 'error': None}

        item = Region(
            name = payload.name.strip(),
            country_id = payload.country_id,
            is_active = payload.active
        )

        session.add(item)
        await session.commit()
        return {'data': {'id': item.id, 'name': item.name, 'is_active': item.is_active}, 'status': 201, 'message': "Region saved successfully! 🎉", 'error': None}
    except Exception as err:
        await session.rollback()
        return {'data': {}, 'status': 500, 'message': "Failed to save region! ❌", 'error': f"{err}"}

@router.put("/country/{country_id}", description="Activate country")
async def activate_country(
        country_id: int,
        payload: ActiveCountry,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        country = (await session.execute(select(Country).where(Country.id == country_id))).scalar_one_or_none()

        if not country:
            return {'data': False, 'status': 404, 'message': "Country Not Found!", 'error': None}
        
        country.is_active = payload.activate
        await session.commit()
        await session.refresh(country)
        return {'data': True, 'status': 200, 'message': "Status updated succesfully!", 'error': None}
    except Exception as err:
        await session.rollback()
        return {'data': False, 'status': 500, 'message': "Server error!", 'error': f"{err}"}
    
@router.put("/region/{region_id}", description="Activate country")
async def activate_country(
        region_id: int,
        payload: ActiveCountry,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        region = (await session.execute(select(Region).where(Region.id == region_id))).scalar_one_or_none()

        if not region:
            return {'data': False, 'status': 404, 'message': "Region Not Found!", 'error': None}
        
        region.is_active = payload.activate

        await session.commit()
        await session.refresh(region)
        return {'data': True, 'status': 200, 'message': "Status updated succesfully!", 'error': None}
    except Exception as err:
        await session.rollback()
        return {'data': False, 'status': 500, 'message': "Server error", 'error': f"{err}"}

@router.get("/admin", description="Get Countries list")
async def get_countries_list(session: AsyncSession = Depends(get_async_session), authorized: bool = Depends(require_api_key)):
    try:
        countries = await session.execute(select(Country).order_by(Country.id.desc()))
        items = countries.scalars().all()
        
        return {
            'data': [
                {
                    'id': item.id,
                    'name': item.name,
                    'is_active': item.is_active
                }
                for item in items
            ],
            'status': 200, 'message': None, 'error': None
        }
    except Exception as err:
        return {'data': [], 'status': 500, 'message': "Server error", 'error': f"{err}"}

@router.get("/admin/country/{country_id}", description="Get regions with country id")
async def get_countries_list_with_id(country_id: int, session: AsyncSession = Depends(get_async_session), authorized: bool = Depends(require_api_key)):
    try:
        country = (await session.execute(select(Country).where(Country.id == country_id))).scalar_one_or_none()
        if not country:
            return {'data': [], 'status': 404, 'message': "Country Not Found!", 'error': None}
        
        regions = (
            await session.execute(
                select(Region)
                .where(Region.country_id == country.id)
                .order_by(Region.id.desc())
            )
        ).scalars().all()
        
        return {
            'data': {
                'id': country.id,
                'name': country.name,
                'regions': [
                    {
                        'id': i.id,
                        'name': i.name,
                        'is_active': i.is_active
                    }
                    for i in (regions or [])
                ]
            }, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return {'data': [], 'status': 500, 'message': "Server error", 'error': f"{err}"}
    
@router.delete("/country/{country_id}", description="Delete Country")
async def delete_country(country_id: int, session: AsyncSession = Depends(get_async_session), authorized: bool = Depends(require_api_key)):
    try:
        countries = await session.execute(
            select(Country)
            .where(Country.id == country_id)
        )
        item = countries.scalar_one_or_none()

        if not item:
            return {'data': False, 'status': 404, 'message': "Country not found!", 'error': None}
        
        await session.delete(item)
        await session.commit()
        return {'data': True, 'status': 200, 'message': "Country successfully removed", 'error': None}
    except ValueError:
        await session.rollback()
        return {'data': False, 'status': 400, 'message': "Invalid value!", 'error': None}
    except Exception as err:
        await session.rollback()
        return {'data': False, 'status': 500, 'message': "Server error", 'error': f"{err}"}

@router.delete("/region/{region_id}", description="Delete Country")
async def delete_region(region_id: int, session: AsyncSession = Depends(get_async_session), authorized: bool = Depends(require_api_key)):
    try:
        countries = await session.execute(
            select(Region)
            .where(Region.id == region_id)
        )
        item = countries.scalar_one_or_none()
        if not item:
            return {'data': False, 'status': 404, 'message': "Region not found!", 'error': None}
        
        await session.delete(item)
        await session.commit()
        return {'data': True, 'status': 200, 'message': "Region successfully removed", 'error': None}
    except ValueError:
        await session.rollback()
        return {'data': False, 'status': 400, 'message': "Invalid value!", 'error': None}
    except Exception as err:
        await session.rollback()
        return {'data': False, 'status': 500, 'message': "Server error", 'error': f"{err}"}