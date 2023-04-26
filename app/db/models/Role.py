from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import DBBaseClass
import uuid


class Role(DBBaseClass):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, unique=True, index=True, default=None)
    name = Column(String, unique=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships:

    def __init__(self, name: str, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            self.public_id = str(uuid.uuid4())
        if name is not None:
            self.name = name.capitalize()

    def __str__(self):
        return f"{self.email} ({self.first_name} {self.last_name}) - {self.public_id}"

    def to_dict(self):
        return dict(
            public_id=self.public_id,
            name=self.name,
            description=self.description
        )
