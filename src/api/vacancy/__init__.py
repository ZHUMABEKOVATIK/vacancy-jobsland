from fastapi import APIRouter

from src.api.vacancy import internship, jobvacancy, one_time_task, opportunities_grants

router = APIRouter(prefix="/vacancy", tags=['Эндпоинты по созданию вакансий'])

router.include_router(jobvacancy.router)
router.include_router(internship.router)
router.include_router(one_time_task.router)
router.include_router(opportunities_grants.router)