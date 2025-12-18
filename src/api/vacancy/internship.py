from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from src.core.auth import get_current_user
from src.database import get_async_session
from src.models.users import Users
from src.models.vacancy import Internship
from src.schemas.vacancy import CreateInternship
from src.core.i18n.notification import get_notification_format
from src.core.bot import BotConfig, get_bot_config
from src.core.i18n.vacancy.internship import get_vacancy_group_format

router = APIRouter(prefix="/internship")

@router.post("/", description="Jan'a internship jaratiw")
async def create_new_internship(
        payload: CreateInternship,
        user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config)
    ):
    try:
        non_auth = HTTPException(status_code=401, detail="You have not filled out the form on your profile.")
        if (
            not user.client.country_id or
            not user.client.region_id or 
            not user.contact
            ):
            raise non_auth
        job = Internship(
            author_id = user.id,
            country_id = payload.country_id,
            region_id = payload.region_id if payload.region_id is not None else None,
            position_title = payload.position_title,
            organization_name = payload.organization_name if payload.organization_name is not None else None,
            requirements = payload.requirements,
            duties = payload.duties,
            conditions = payload.conditions if payload.conditions is not None else None,
            address = payload.address,
            salary = payload.salary,
            contact = payload.contact,
            additional_info = payload.additional_info if payload.additional_info is not None else None,
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
            moderation_cfg = await botcfg.send_message_group(post_id=job.id, text=moderation_msg, vacancy_type="intern")
            job.group_message_id = moderation_cfg.message_id
            job.group_chat_id = moderation_cfg.chat_id
        except Exception as e:
            print(f"Bot send error: {e}")

        await session.commit()
        return {"data": "Successfull", "ok": True, "id": job.id}
    except HTTPException:
        await session.rollback()
        raise
    except Exception as err:
        await session.rollback()
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/mine", description="My vacances list")
async def get_my_vacancies(
        user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ):
    try:
        exiting = await session.execute(
            select(Internship)
            .where(Internship.author_id == user.id)
            .where(Internship.is_delete.is_(False))
            .options(
                selectinload(Internship.country),
                selectinload(Internship.region),
            )
            .order_by(Internship.id.desc())
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
                "position_title": item.position_title,
                "organization_name": item.organization_name,
                "address": item.address,
                "requirements": item.requirements,
                "duties": item.duties,
                "conditions": item.conditions,
                "salary": item.salary,
                "contact": item.contact,
                "additional_info": item.additional_info,
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
        print(f"Server error: {err}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.put("/{vacancy_id}", description="Vakanciyani o'zgertiw", status_code=200)
async def update_vacancy(
        vacancy_id: int,
        payload: CreateInternship,
        user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
    ):
    try:
        exiting = await session.execute(
            select(Internship)
            .where(Internship.id == vacancy_id)
            .where(Internship.is_delete.is_(False))
            .options(
                selectinload(Internship.country),
                selectinload(Internship.region),
            )
            .order_by(Internship.id.desc())
        )
        job = exiting.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Vacancy not found!")
        if job.author_id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This vacancy does not belong to you")
        
        job.country_id = payload.country_id
        job.region_id = payload.region_id if payload.region_id is not None else None
        job.position_title = payload.position_title
        job.organization_name = payload.organization_name if payload.organization_name is not None else None
        job.address = payload.address
        job.requirements = payload.requirements
        job.duties = payload.duties
        job.conditions = payload.conditions if payload.duties is not None else None
        job.salary = payload.salary
        job.contact = payload.contact
        job.additional_info = payload.additional_info if payload.additional_info is not None else None

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
            select(Internship)
            .where(Internship.id == vacancy_id)
            .where(Internship.is_delete.is_(False))
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