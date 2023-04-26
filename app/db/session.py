# Configuration for SessionLocal to be used across the project
# SQLALCHEMY_DATABASE_URL defines the connection to the database
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define Database connection
def local_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
