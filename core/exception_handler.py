from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
import traceback

from app.common.DefaultLogger import configure_logger

log = configure_logger("errors.log")


def define_handler_exception(app: FastAPI):
    # This dispatch all general Exceptions
    @app.exception_handler(Exception)
    async def default_handler_exception(request: Request, exc):
        log.error(f"New exception: {exc}")
        log.error(f"{request.client} ")
        log.error(f"{request.method} {request.url}")
        log.error(f"{request.headers}")
        log.error(f"{traceback.format_exc(-5)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=dict(error=f"{exc}"))


