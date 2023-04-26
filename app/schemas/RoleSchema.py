from pydantic import BaseModel


class Base(BaseModel):
    name: str
    description: str


class Create(Base):
    pass


class Public(Base):
    public_id: str
