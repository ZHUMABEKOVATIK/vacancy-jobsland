from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": f"Server error: {str(exc)}"},
        )
