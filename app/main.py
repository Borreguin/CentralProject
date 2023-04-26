import uvicorn
from fastapi import FastAPI

# import general settings
from app.core.log_after_request import log_after_request
from app.core.config import settings
from app.core.exception_handler import define_handler_exception

# import endpoints
from app.endpoints import UserEndpoint, RoleEndpoint

# import database models:
from app.db.session import engine
from app.db.base import DBBaseClass


def include_routes(app):
    # To include EndPoints:
    app.include_router(UserEndpoint.router)
    app.include_router(RoleEndpoint.router)


def create_tables():
    # generate automatically tables in database
    # the corresponding tables must be imported in app.db.base.py
    DBBaseClass.metadata.create_all(bind=engine)


def define_loggers(app):
    # adds general handler exception if something was not controled
    define_handler_exception(app)
    # adds logger for requests
    log_after_request(app)


def create_application() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    define_loggers(app)
    include_routes(app)
    create_tables()
    return app


api = create_application()

