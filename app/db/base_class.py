# Declarative class that allows the persistence to the database:
# This abstract class will inherit CRUD operations

from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class DBBaseClass:
    id: Any
    __name__: str

    # to generate tablename from classname
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


