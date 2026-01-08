from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from typing import AsyncGenerator
from dotenv import load_dotenv
load_dotenv()
import os

DB_URL = f"postgresql+asyncpg://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWD')}@localhost/{os.getenv('DB_NAME')}"
engine = create_async_engine(DB_URL, echo=False)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

from src.models.locations import Country, Region
from src.models.industry import Industry
from src.models.users import Users, Clients
from src.models.channels import Channels
from src.models.vacancy import JobVacancy, Internship, OneTimeTask, OpportunitiesGrants, StatusEnum

# Use connection
async def async_main():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
