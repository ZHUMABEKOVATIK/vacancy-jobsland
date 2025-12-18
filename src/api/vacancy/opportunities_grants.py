from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pathlib import Path

from src.core.auth import get_current_user
from src.database import get_async_session
from src.models.users import Users
from src.models.vacancy import OpportunitiesGrants
from src.core.bot import get_bot_config, BotConfig
from src.core.files import save_image
from src.core.i18n.notification import get_notification_format
from src.core.i18n.vacancy.opportunities_grants import get_vacancy_group_format

router = APIRouter(prefix="/opportunities_grants")

@router.post("/")
async def create_opportunities_grants(
        request: Request,
        country_id: int = Form(...),
        region_id: int | None = Form(None),
        content: str = Form(...),
        contact: str = Form(...),
        img: UploadFile | None = File(None),
        user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config)
    ):
    try:
        img_path: str | None = None
        if img is not None:
            img_path = await save_image(img, max_mb=20)

        job = OpportunitiesGrants(
            country_id = country_id,
            region_id = region_id,
            author_id = user.id,
            img_path = img_path,
            content = content,
            contact = contact
        )
        session.add(job)
        await session.flush()

        try:
            msg = get_notification_format(request_id=job.id, lang_code=user.language_code)
            await botcfg.send_message(chat_id=user.telegram_id, message=msg)
        except Exception as e:
            print(f"Bot send error: {e}")
        
        try:
            moderation_msg = await get_vacancy_group_format(post=job)
            moderation_cfg = await botcfg.send_photo_group(
                post_id=job.id,
                text=moderation_msg, 
                vacancy_type="opgts", 
                photo_url=(f"{request.base_url}{img_path}" if img_path is not None else None)
            )

            job.group_message_id = moderation_cfg.message_id
            job.group_chat_id = moderation_cfg.chat_id
        except Exception as e:
            print(f"Bot send error: {e}")

        await session.commit()
        await session.refresh(job)
        return {'data': "Successfull", 'status': True}
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail=f"Internal server error.")
    
@router.get("/mine", description="My vacances list")
async def get_my_vacancies(
        request: Request,
        user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ):
    try:
        exiting = await session.execute(
            select(OpportunitiesGrants)
            .where(OpportunitiesGrants.author_id == user.id)
            .where(OpportunitiesGrants.is_delete.is_(False))
            .options(
                selectinload(OpportunitiesGrants.country),
                selectinload(OpportunitiesGrants.region),
            )
            .order_by(OpportunitiesGrants.id.desc())
        )
        items = exiting.scalars().all()
        return {'data': [
            {
                'id': item.id,
                'location': {
                    'country': {
                        'id': item.country_id,
                        'name': item.country.name
                    },
                    'region': {'id': item.region_id, 'name': item.region.name} if item.region_id is not None else None
                },
                "content": item.content,
                "img": (f"{request.base_url}{item.img_path}" if item.img_path is not None else None),
                "contact": item.contact,
                'status': {
                    'status': item.status,
                    'reason': item.reject_reason
                },
                "created_at": {
                    "day": item.created_at.day,
                    "month": item.created_at.month,
                    "year": item.created_at.year,
                    "hour": item.created_at.hour,
                    "minute": item.created_at.minute 
                }
            }
            for item in items
        ]}
    except Exception as err:
        raise HTTPException(status_code=500, detail="server error")
    
@router.put("/{vacancy_id}", description="Vakanciyani o'zgertiw", status_code=200)
async def update_vacancy(
        request: Request,
        vacancy_id: int,
        country_id: int = Form(...),
        region_id: int | None = Form(None),
        content: str = Form(...),
        contact: str = Form(...),
        img: UploadFile | None = File(None),
        user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
    ):
    try:
        exiting = await session.execute(
            select(OpportunitiesGrants)
            .where(OpportunitiesGrants.id == vacancy_id)
            .where(OpportunitiesGrants.is_delete.is_(False))
            .options(
                selectinload(OpportunitiesGrants.country),
                selectinload(OpportunitiesGrants.region),
            )
            .order_by(OpportunitiesGrants.id.desc())
        )
        job = exiting.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Vacancy not found!")
        if job.author_id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This vacancy does not belong to you")
        job.country_id = country_id
        if region_id is not None:
            job.region_id = region_id
        job.content = content
        job.contact = contact
        new_img_path: str | None = None
        if new_img_path is not None:
            new_img_path = await save_image(img, max_mb=20)
            try:
                if job.img_path:
                    old = Path(job.img_path)
                    if old.exists():
                        old.unlink(missing_ok=True)
            except Exception:
                pass
        await session.commit()
        return {"data": "Successfull", "ok": True, "id": job.id}
    except HTTPException:
        await session.rollback()
        raise
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    
@router.delete("/{vacancy_id}")
async def delete_vacancy(
        vacancy_id: int,
        user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ):
    try:
        exiting = await session.execute(
            select(OpportunitiesGrants)
            .where(OpportunitiesGrants.id == vacancy_id)
            .where(OpportunitiesGrants.is_delete.is_(False))
        )
        job = exiting.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Vacancy not found!")
        if job.author_id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This vacancy does not belong to you")
        
        job.is_delete = True
        await session.commit()
        return {"data": "Successfull", "ok": True, "id": job.id}
    except HTTPException:
        await session.rollback()
        raise
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail="Internal server error.")