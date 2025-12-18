from fastapi import APIRouter
from src.api import users, vacancy, channels, languages, world, worldAdmin, statistic, industry, admin
from src.api.vacancy import moderation

routers = APIRouter()

routers.include_router(languages.router)
routers.include_router(world.router)
routers.include_router(users.router)
routers.include_router(vacancy.router)
routers.include_router(channels.router)
routers.include_router(moderation.router)
routers.include_router(worldAdmin.router)
routers.include_router(statistic.router)
routers.include_router(industry.router)
routers.include_router(admin.router)