from sqlalchemy import Boolean, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.common.util import get_hashed_text, verify_hashed_text
from app.db.base_class import DBBaseClass
import uuid

user_role = Table('user_role',
                  DBBaseClass.metadata,
                  Column('user_id', Integer, ForeignKey("user.id")),
                  Column('role_id', Integer, ForeignKey("role.id")))


class User(DBBaseClass):
    __tablename__ = 'user'
    # Fields:
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, unique=True, index=True, default=None)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships:
    roles = relationship("Role", secondary=user_role, backref="users")

    def __init__(self, password, *args, **values):
        super().__init__(*args, **values)
        if self.public_id is None:
            self.public_id = str(uuid.uuid4())
        if password is not None:
            self.set_password(password)

    def verify_password(self, to_verify) -> bool:
        return verify_hashed_text(to_verify, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = get_hashed_text(password)

    def __str__(self):
        return f"{self.email} ({self.first_name} {self.last_name}) - {self.public_id}"

    def to_dict(self):
        return dict(
            public_id=self.public_id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            roles=[r.to_dict() for r in self.roles]
        )
