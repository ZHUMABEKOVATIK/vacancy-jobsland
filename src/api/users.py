from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from pydantic import BaseModel

from src.core.bot import BotConfig, get_bot_config
from src.database import get_async_session
from src.core.telegram_webapp import verify_init_data
from src.core.jwt import create_access_token, create_refresh_token
from src.models.users import Users, Clients
from src.schemas.users import CreateAccountForm, IsAuthUser, TelegramWebAppAuthIn, TokenPairOut, UpdateProfile, UpdateUserLanguage, GeneralProfileOut
from src.core.auth import get_current_user, require_api_key
from src.logs.error_handler import handle_exceptions

router = APIRouter(prefix="/users", tags=['Authorization'])

class ResponseOut(BaseModel):
    data: dict | list
    status: int
    message: str | None
    error: str | None

@router.post("/telegram/webapp/auth", description="InitData ja'rdeminde access token ha'm refresh token alinadi", response_model=TokenPairOut)
async def telegram_webapp_auth(body: TelegramWebAppAuthIn, session: AsyncSession = Depends(get_async_session)):
    try:
        verified = verify_init_data(body.init_data)
        tg = verified.get("user")
        tg_id = int(tg["id"])
        res = await session.execute(select(Users).where(Users.telegram_id == tg_id))
        user = res.scalar_one_or_none()

        if not user:
            try:
                user = Users(telegram_id=tg_id)
                session.add(user)
                await session.flush()
                session.add(Clients(user_id=user.id))
                await session.commit()
            except Exception as err:
                print(f"Server error: {err}")
                await session.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot create user")
        else:
            cres = await session.execute(select(Clients).where(Clients.user_id == user.id))
            if not cres.scalar_one_or_none():
                session.add(Clients(user_id=user.id))
                await session.commit()
        
        access = await create_access_token({"user_id": user.id, "telegram_id": user.telegram_id})
        refresh = await create_refresh_token({"user_id": user.id, "telegram_id": user.telegram_id})
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail=f"Internal server error.")

@router.post("/telegram/bot/auth", description="Bot ushin api")
async def telegram_auth(
        payload: CreateAccountForm,
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        bot_id = await botcfg.get_id()
        if payload.bot_id != bot_id:
            raise HTTPException(status_code=400, detail="Siz basqa bottan soraw jolladin'iz!")
        user = Users(
            telegram_id=payload.user_id,
            language_code=payload.language_code
        )
        session.add(user)
        await session.flush()
        client = Clients(
            user_id=user.id
        )
        session.add(client)
        await session.commit()
        return {'data': 'successfull', 'status': True}
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail=f"Internal server error.")

@router.post("/telegram/bot/is_auth", description="Bot ushin api")
async def is_auth_user(
        payload: IsAuthUser,
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        if not payload.bot_id and not payload.user_id:
            raise HTTPException(status_code=400, detail="Soraw qate jiberildi")
        
        bot_id = await botcfg.get_id()
        if payload.bot_id != bot_id:
            raise HTTPException(status_code=400, detail="Siz basqa bottan soraw jiberdin'iz!")
        
        exiting = await session.execute(select(Users).where(Users.telegram_id == int(payload.user_id)))
        user_data = exiting.scalar_one_or_none()

        if not user_data:
            return {'data': True, 'is_auth': False, 'lang_code': None}
        
        return {'data': True, 'is_auth': True, 'lang_code': user_data.language_code}
    except Exception as err:
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail=f"Internal server error.")

@router.put("/telegram/bot/language", description="Telegram arqali tildi o'zgertiw")
async def update_user_language(
        payload: UpdateUserLanguage, 
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        if not payload.bot_id and not payload.user_id and not payload.code:
            raise HTTPException(status_code=400, detail="Soraw qate jiberildi")
        bot_id = await botcfg.get_id()
        if payload.bot_id != bot_id:
            return {'data': False}
        exiting = await session.execute(select(Users).where(Users.telegram_id == int(payload.user_id)))
        user_data = exiting.scalar_one_or_none()
        if not user_data:
            raise HTTPException(status_code=400, detail="Bul paydalaniwshi dizimnen o'tpegen!")
        user_data.language_code = payload.code
        await session.commit()
        return {'data': True}
    except HTTPException:
        await session.rollback()
        raise
    except SQLAlchemyError as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail=f"Internal database error.")
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.post("/telegram/bot/get/language")
async def get_user_language(
        payload: IsAuthUser,
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config),
        authorized: bool = Depends(require_api_key)
    ):
    try:
        if not payload.bot_id and not payload.user_id:
            raise HTTPException(status_code=400, detail="Soraw qate jiberildi")
        bot_id = await botcfg.get_id()
        if payload.bot_id != bot_id:
            return {'data': False}
        exiting = await session.execute(select(Users).where(Users.telegram_id == int(payload.user_id)))
        user_data = exiting.scalar_one_or_none()
        if not user_data:
            raise HTTPException(status_code=400, detail="Bul paydalaniwshi dizimnen o'tpegen!")
        return {'data': user_data.language_code}
    except HTTPException:
        await session.rollback()
        raise
    except SQLAlchemyError as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail=f"Internal database error.")
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/me", description="Paydalaniwshi haqqinda mag'liwmatlardi aliw", response_model=GeneralProfileOut)
async def get_me(user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    client = user.client

    country = {
        'id': client.country_id,
        'name': client.country.name
    } if (client and client.country) else None

    region = {
        'id': client.region_id,
        'name': client.region.name
    } if (client and client.region) else None

    industry = {
        'id': client.industry_id,
        'name': client.industry.name
    } if (client and client.industry) else None
    
    return {
        'data': {
            'full_name': user.full_name,
            'language': user.language_code,
            'company_name': user.client.company_name,
            "location": {
                "country": country,
                "region": region,
            },
            'contact': user.contact,
            'telegram_id': user.telegram_id,
            'industry': industry
        }, 'status': 200, 'message': None, 'error': None
    }

@router.put("/me", description="Paydalaniwshi haqqinda mag'liwmatlarin o'zgertiw", response_model=GeneralProfileOut)
async def update_me(
        payload: UpdateProfile,
        user: Users = Depends(get_current_user), 
        session: AsyncSession = Depends(get_async_session)
    ):
    try:
        if payload.full_name is not None:
            user.full_name = payload.full_name

        if payload.contact is not None:
            user.contact = payload.contact
        
        if payload.language_code is not None:
            user.language_code = payload.language_code

        if payload.company_name is not None:
            if not user.client:
                raise HTTPException(status_code=400, detail="Client profile not found")
            user.client.company_name = payload.company_name

        if payload.country_id is not None:
            if not user.client:
                raise HTTPException(status_code=400, detail="Client profile not found")
            user.client.country_id = payload.country_id
            
        if payload.region_id is not None:
            if not user.client:
                raise HTTPException(status_code=400, detail="Client profile not found")
            user.client.region_id = payload.region_id
        
        if payload.industry_id is not None:
            if not user.client:
                raise HTTPException(status_code=400, detail="Client profile not found")
            user.client.industry_id = payload.industry_id

        await session.flush()
        await session.commit()

        client = user.client

        country = {
            'id': client.country_id,
            'name': client.country.name
        } if (client and client.country) else None
        region = {
            'id': client.region_id,
            'name': client.region.name
        } if (client and client.region) else None
        industry = {
            'id': client.industry_id,
            'name': client.industry.name
        } if (client and client.industry) else None

        return {'data': {
            'full_name': user.full_name,
            'language': user.language_code,
            'company_name': user.client.company_name,
            "location": {
                "country": country,
                "region": region,
            },
            'contact': user.contact,
            'telegram_id': user.telegram_id,
            'industry': industry
        }, 'status': 200, 'message': "Profile updated succesfully.", 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Profile Update Error")

