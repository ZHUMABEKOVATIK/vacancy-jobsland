from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database import async_main, engine
from src.core.set_countries_base import set_countries_to_base_with_file

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start...")
    await async_main()
    await set_countries_to_base_with_file()
    yield
    await engine.dispose()
    print("End...")