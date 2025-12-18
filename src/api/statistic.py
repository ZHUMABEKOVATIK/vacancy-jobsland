import aiohttp
from fastapi import APIRouter, Depends, Query, Response, Request
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from sqlalchemy.orm import selectinload

from src.core.bot import BotConfig, get_bot_config
from src.models.users import Users, Clients
from src.models.vacancy import JobVacancy, Internship, OneTimeTask, OpportunitiesGrants, StatusEnum
from src.models.industry import Industry
from src.database import get_async_session
from src.core.auth import require_api_key
from src.schemas.statistic import GetUserPost, GetUserProfile, StatVacancyOut, StatVacancyMonthOut
from src.schemas.industry import IndustryResponse
from src.logs.error_handler import handle_exceptions

router = APIRouter(prefix="/stats", tags=['Статистика'])

MODEL_TITLES = {
    "job_vacancies": "Вакансии",
    "internship": "Стажировка",
    "one_time_task": "Разовая задача/проект",
    "opportunities_grants": "Возможности и Гранты"
}
ICONS = {
    "job_vacancies": "MdWork",
    "internship": "HiBriefcase",
    "one_time_task": "FaRegCheckCircle",
    "opportunities_grants": "FaRegLightbulb"
}
COLORS = {
    "job_vacancies": "#267fe9",
    "internship": "#ffc12e",
    "one_time_task": "#ff5636",
    "opportunities_grants": "#48d3ff"
}

ELEMENTARY_MODELS = {
    "job_vacancies": JobVacancy,
    "internship": Internship,
    "one_time_task": OneTimeTask,
    "opportunities_grants": OpportunitiesGrants
}

LANGUAGE = {
    "eng": "English",
    "rus": "Русский",
    "uzb": "Oʻzbekcha",
    "kaz": "Қазақша",
    "kaa": "Qaraqalpaqsha",
    "kgz": "Кыргызча",
    "tjk": "Тоҷикӣ",
    "aze": "Azərbaycan",
    "tkm": "Türkmençe"
}

FIELDS = [
    "position_title",
    "organization_name",
    "address",
    "requirements",
    "duties",
    "work_schedule",
    "salary",
    "contact",
    "additional_info",
    "conditions",
    "who_needed"
    "task_description"
    "deadline",
    "content",
    "img_path",
    "status",
    "reject_reason"
]

@router.get('/vacancy_tabs', description="Vacancy Tabs")
async def get_vacancy_tabs(authorized: bool = Depends(require_api_key)):
    TABS = ["job_vacancies", "internship", "one_time_task", "opportunities_grants"]

    TAB_NAMES = [
        ("job_vacancies", "Вакансии"), 
        ("internship", "Стажировка"), 
        ("one_time_task", "Разовая задача/проект"), 
        ("opportunities_grants", "Возможности и Гранты")
    ]

    return {'data': {'tabs': TABS, 'offical': TAB_NAMES}, 'status': 200, 'message': None, 'error': None}

@router.get('/vacancies', response_model=StatVacancyOut)
async def vacancy_stat(session: AsyncSession = Depends(get_async_session), authorized: bool = Depends(require_api_key)):
    try:
        MODELS = [JobVacancy, Internship, OneTimeTask, OpportunitiesGrants]
        
        results = []

        for item in MODELS:
            total = await session.scalar(select(func.count()).select_from(item))
            approved = await session.scalar(
                select(func.count()).select_from(item).where(item.status == StatusEnum.APPROVED)
            )
            rejected = await session.scalar(
                select(func.count()).select_from(item).where(item.status == StatusEnum.REJECTED)
            )

            results.append({
                'code': f"{item.__table__.name}",
                'title': MODEL_TITLES[item.__table__.name],
                'length': total or 0,
                'icon': ICONS[item.__table__.name],
                'color': COLORS[item.__table__.name],
                'approved': approved or 0,
                'rejected': rejected or 0
            })

        return {'data': results, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return {'data': [], 'status': 500, 'message': f"Server error", 'error': f"{err}"}
    
@router.get('/vacancies/elementary/{stat_code}', response_model=StatVacancyMonthOut)
async def vacancy_stat_elementary(stat_code: str, session: AsyncSession = Depends(get_async_session), authorized: bool = Depends(require_api_key)):
    try:
        MODEL = ELEMENTARY_MODELS.get(stat_code)
        
        if not MODEL:
            return {'data': [], 'status': 404, 'message': "Wrong stat type", 'error': None}

        result = [{'month': i, 'value': 0} for i in range(1, 13)]

        query = (
            select(
                func.extract('month', MODEL.created_at).label('month'),
                func.count().label('total')
            )
            .where(func.extract('year', MODEL.created_at) == 2025)
            .group_by('month')
            .order_by('month')
        )

        rows = await session.execute(query)

        for month, total in rows:
            for i in result:
                if i['month'] == int(month):
                    i['value'] = total

        return {'data': result, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return {'data': [], 'status': 500, 'message': f"Server error", 'error': f"{err}"}
    
@router.get("/industry", response_model=IndustryResponse)
async def get_industry_stat(
    session: AsyncSession = Depends(get_async_session),
    authorized: bool = Depends(require_api_key),
    limit: int | None = Query(None, description="Количество элементов на странице"),
    offset: int | None = Query(None, description="Смещение для следующей страницы")
):
    try:
        stmt = (
            select(
                Industry.id,
                Industry.name,
                func.count(Clients.id).label("client_count")
            )
            .outerjoin(Clients, Industry.id == Clients.industry_id)
            .group_by(Industry.id, Industry.name)
            .order_by(func.count(Clients.id).desc())
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await session.execute(stmt)
        data = [dict(row) for row in result.mappings().all()]

        users_count = await session.scalar(select(func.count()).select_from(Clients))

        total_industries = await session.scalar(select(func.count()).select_from(Industry))

        return {
            'data': {
                'data': data,
                'total': total_industries,
                'users_count': users_count,
                'limit': limit,
                'offset': offset
            },
            'status': 200,
            'message': None,
            'error': None
        }

    except Exception as err:
        return await handle_exceptions(session, [], err, "Industry stat error!")
    
@router.get("/users")
async def get_users_stat_list(
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key),
    ):
    try:
        users = (await session.execute(
            select(Users).order_by(Users.id)
        )).scalars().all()


        result = []
        for user in users:
            client = user.client

            result.append({
                'id': user.id,
                'telegram_id': user.telegram_id,
                'full_name': user.full_name,
                'company_name': client.company_name,
                'contact': user.contact
            })

        return {'data': result, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Error in users list")

@router.get("/photo/{telegram_id}")
async def get_photo_with_file_id(
        telegram_id: int,
        request: Request,
        authorized: bool = Depends(require_api_key),
        botcfg: BotConfig = Depends(get_bot_config)
    ):
    bot = await botcfg.getBot()
    base_url = str(request.base_url).rstrip("/")
    default_path = Path(__file__).resolve().parent.parent / "media" / "userprofile.png"
    try:
        chat = await bot.get_chat(telegram_id)

        if chat.photo:
            file = await bot.get_file(chat.photo.big_file_id)
            photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(photo_url) as resp:
                    content = await resp.read()
            return Response(content, media_type="image/jpeg")
        else:
            with open(default_path, "rb") as f:
                content = f.read()
            return Response(content, media_type="image/png")
    except Exception as err:
        print(f"[get_photo_with_file_id] Error: {err}")
        with open(default_path, "rb") as f:
            content = f.read()
        return Response(content, media_type="image/png")

@router.post("/user/profile")
async def get_one_user(
        payload: GetUserProfile,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key),
        botcfg: BotConfig = Depends(get_bot_config)
    ):
    try:
        user = (await session.execute(
                select(Users)
                .where(Users.id == payload.id)
                .where(Users.telegram_id == payload.telegram_id)
                .options(selectinload(Users.client))
            )
        ).scalar_one_or_none()

        if not user or not user.client:
            return {'data': {}, 'status': 404, 'message': "User not found.", 'error': None}
        
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
            'id': user.id,
            'telegram_id': user.telegram_id,
            'full_name': user.full_name,
            'language': LANGUAGE.get(user.language_code),
            'contact': user.contact,
            'company_name': client.company_name,
            'country': country,
            'region': region,
            'industry': industry,
            'created_at': user.created_at 
        }, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Get profile error!")

@router.post("/client/posts")
async def get_client_posts_list(
        payload: GetUserProfile,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key),
    ):
    try:
        user = (await session.execute(
                select(Users)
                .where(Users.id == payload.id)
                .where(Users.telegram_id == payload.telegram_id)
                .options(selectinload(Users.client))
            )
        ).scalar_one_or_none()

        if not user or not user.client:
            return {'data': {}, 'status': 404, 'message': "Client not found.", 'error': None}
        
        MODELS = [JobVacancy, Internship, OneTimeTask, OpportunitiesGrants]
        result = {}

        for model in MODELS:
            slt = slice(15)

            job = (
                await session.execute(
                    select(model)
                    .where(model.author_id == user.id)
                    .order_by(model.id.desc())
                    .limit(1)
                )
            ).scalars().first()

            if job:
                name_field = (
                    getattr(job, "position_title", None)
                    or getattr(job, "who_needed", None)
                    or getattr(job, "content", None)
                )

                name = name_field[slt] if name_field else "Untitled"

                result[model.__tablename__] = {
                    "id": job.id,
                    "name": name,
                    "created_at": job.created_at,
                }
            else:
                result[model.__tablename__] = None

        return {'data': result, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Get posts error!")
    
@router.post("/client/post")
async def get_client_post(
        payload: GetUserPost,
        session: AsyncSession = Depends(get_async_session),
        authorized: bool = Depends(require_api_key),
    ):
    try:
        if payload.vacancy_type.lower() not in list(ELEMENTARY_MODELS.keys()):
            return {'data': {}, 'status': 404, 'message': "Wrong vacancy type.", 'error': None}
        
        MODEL = ELEMENTARY_MODELS.get(payload.vacancy_type.lower())
        job = (
            await session.execute(
                select(MODEL)
                .where(MODEL.id == payload.id)
                .limit(1)
            )
        ).scalars().first()

        if not job:
            return {
                'data': {},
                'status': 404,
                'message': "Post not found.",
                'error': None
            }
        
        country = {
            'id': job.country_id,
            'name': job.country.name
        } if (job and job.country) else None
        region = {
            'id': job.region_id,
            'name': job.region.name
        } if (job and job.region) else None
        
        data = {
            "id": job.id,
            "country": country,
            "region": region,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }

        for field in FIELDS:
            if hasattr(job, field):
                data[field] = getattr(job, field)

        return {'data': data, 'status': 200, 'message': None, 'error': None}
    except Exception as err:
        return await handle_exceptions(session, {}, err, "Get posts error!")
    
