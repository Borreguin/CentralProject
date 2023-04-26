from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
import traceback

from app.common.DefaultLogger import configure_logger

log = configure_logger("app_activity.log")


def log_after_request(app: FastAPI):
    # This logs any activity of the app
    @app.middleware("http")
    async def log_activity_for_this_call(request: Request, call_next):
        response = await call_next(request)
        log.info(f"{request.client.host}: {request.method} {request.url} [{response.status_code}]")
        return response



