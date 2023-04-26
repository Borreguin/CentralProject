from typing import List

from pydantic import BaseModel, EmailStr


class Base(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class Create(Base):
    password: str


class Public(Base):
    public_id: str
    roles: List[dict]
