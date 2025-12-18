from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update

from pydantic import BaseModel
from typing import Literal, Type

from src.core.bot import BotConfig, get_bot_config
from src.core.auth import require_api_key
from src.database import get_async_session
from src.models.vacancy import JobVacancy, StatusEnum, Internship, OneTimeTask, OpportunitiesGrants
from src.models.channels import Channels
from src.core.i18n.notification import get_reject_format, get_approve_format

from src.core.i18n.vacancy.jobvacancy import get_vacancy_channel_format as fmt_job
from src.core.i18n.vacancy.internship import get_vacancy_channel_format as fmt_intern
from src.core.i18n.vacancy.one_time_task import get_vacancy_channel_format as fmt_ot
from src.core.i18n.vacancy.opportunities_grants import get_vacancy_channel_format as fmt_opg
from src.core.i18n.vacancy import make_channel_post

router = APIRouter(prefix="/moderation", tags=['Moderation'])

class ApproveIn(BaseModel):
    vacancy_id: int
    moderator_tid: int
    vacancy_type: str

class RejectIn(BaseModel):
    vacancy_id: int
    moderator_tid: int
    reason: str
    vacancy_type: str

VacancyType = Literal["job", "intern", "otits", "opgts"]

MODEL_BY_TYPE: dict[VacancyType, Type] = {
    "job": JobVacancy,
    "intern": Internship,
    "otits": OneTimeTask,
    "opgts": OpportunitiesGrants,
}

@router.post("/approve")
async def approve_vacancy(
        payload: ApproveIn,
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config),
        req_api_key = Depends(require_api_key)
    ):
    try:
        model = MODEL_BY_TYPE.get(payload.vacancy_type)  # type: ignore[arg-type]
        if model is None:
            raise HTTPException(status_code=400, detail="Wrong vacancy type")

        res  = await session.execute(select(model).where(model.id == payload.vacancy_id))
        job = res.scalar_one_or_none()
        if not job:
            raise HTTPException(404, "Vacancy not found")
        if job.status != StatusEnum.NEW:
            raise HTTPException(409, "Already resolved")
        
        job.status = StatusEnum.APPROVED
        job.moderator_id = payload.moderator_tid

        q = select(Channels).where(Channels.country_id == job.country_id)
        if getattr(job, "region_id", None) is not None:
            q = q.where(Channels.region_id == job.region_id)
        channel = (await session.execute(q)).scalar_one_or_none()
        
        if not channel:
            await session.commit()
            return {"ok": True, "published": False, "reason": "channel_not_found"}

        try:
            chat_id = await botcfg.get_chat_id(channel.channel_url)
            msgw = await make_channel_post(payload.vacancy_type, lang_code=chat_id, post=job)
            sending = await botcfg.send_post(chat_id=chat_id, post=msgw)
            

            job.channel_chat_id = sending.chat_id
            job.channel_message_id = sending.message_id

            try:
                chat_cfg = await botcfg.get_user_with_chat_id(telegram_id=sending.chat_id)
                mod_text = get_approve_format(job.id, job.user.language_code, chat_cfg.username)
                await botcfg.send_message(chat_id=job.user.telegram_id, message=mod_text)
            except Exception as err:
                print(f"Approve Notification failed: {err}")
        except Exception as e:
            print(f"Bot send error: {e}")
            await session.commit()
            return {"ok": True, "published": False}

        await session.commit()
        return {"ok": True, "published": True, "chat_id": job.channel_chat_id, "message_id": job.channel_message_id}
    except Exception as err:
        raise HTTPException(status_code=500, detail="Server error")
    
@router.post("/reject")
async def reject_vacancy(
        payload: RejectIn,
        session: AsyncSession = Depends(get_async_session),
        botcfg: BotConfig = Depends(get_bot_config),
        req_api_key = Depends(require_api_key)
    ):
    try:
        model = MODEL_BY_TYPE.get(payload.vacancy_type)  # type: ignore[arg-type]
        if model is None:
            raise HTTPException(status_code=400, detail="Wrong vacancy type")
        
        upd = (
            update(model)
            .where(model.id == payload.vacancy_id, model.status == StatusEnum.NEW)
            .values(
                status=StatusEnum.REJECTED,          
                moderator_id=payload.moderator_tid, 
                reject_reason=payload.reason,
            )
            .returning(model.id)
        )
        row = await session.execute(upd)
        updated = row.scalar_one_or_none()
        if not updated:
            exists = await session.execute(select(model.id).where(model.id == payload.vacancy_id))
            if exists.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Already resolved")
            raise HTTPException(status_code=404, detail="Vacancy not found")
        
        await session.commit()

        res = await session.execute(
            select(model)
            .where(model.id == payload.vacancy_id)
            .options(selectinload(model.user))
        )
        job = res.scalar_one_or_none()
        if job is None or job.user is None:
            return {"ok": True, "message": "Rejected", "notified": False}
        try:
            msg = get_reject_format(job.id, lang_code=job.user.language_code, reason=payload.reason)
            await botcfg.send_message(chat_id=job.user.telegram_id, message=msg)
            notified = True
        except Exception as err:
            print(f"Bot send error: {err}")
            notified = False

        return {"ok": True, "message": "Rejected", "notified": notified}
    except HTTPException:
        await session.rollback()
        raise
    except SQLAlchemyError as err:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {err}")
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Server error")