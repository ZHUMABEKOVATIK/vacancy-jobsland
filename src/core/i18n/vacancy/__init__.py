# core/i18n/vacancy/__init__.py
from typing import Literal, Callable
from src.core.i18n.vacancy.vacancy_types import TgPost
from src.core.i18n.vacancy.jobvacancy import get_vacancy_channel_format as fmt_job
from src.core.i18n.vacancy.internship import get_vacancy_channel_format as fmt_intern
from src.core.i18n.vacancy.one_time_task import get_vacancy_channel_format as fmt_ot
from src.core.i18n.vacancy.opportunities_grants import get_vacancy_channel_format as fmt_opg

VacancyType = Literal["job", "intern", "otits", "opgts"]

FMT_BY_TYPE: dict[VacancyType, Callable[..., TgPost]] = {
    "job": fmt_job,
    "intern": fmt_intern,
    "otits": fmt_ot,
    "opgts": fmt_opg,
}

async def make_channel_post(vac_type: VacancyType, *, lang_code: str, post) -> TgPost:
    return await FMT_BY_TYPE[vac_type](lang_code=lang_code, post=post)
