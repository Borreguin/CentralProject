from typing import List
from sqlalchemy.orm import Session

from app.schemas import RoleSchema
from app.db.models.Role import Role
from app.db.models.User import User


def get_by_id(db: Session, user_id: int) -> Role:
    return db.query(Role).filter(Role.id == user_id).first()


def get_by_name(db: Session, name: str) -> Role:
    return db.query(Role).filter(Role.name == name.capitalize()).first()


def get_by_public_id(db: Session, public_id: str) -> Role:
    return db.query(Role).filter(Role.public_id == public_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()


def create(db: Session, role: RoleSchema.Create) -> Role:
    db_role = Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return db_role


def add_role_to_user(db: Session, db_role: Role, db_user: User) -> User:
    db_user.roles.append(db_role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
