from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from src.core.cors import setup_cors
from src.core.lifespan import lifespan
from src.api import routers

BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = BASE_DIR / "media"

app = FastAPI(title="AumetaJobs",lifespan=lifespan, version="1.5.2")
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="static")

app.include_router(routers)

# middlewares
setup_cors(app)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"{exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error."},
    )

if __name__ == "__main__":
    uvicorn.run(app=app, port=8010)