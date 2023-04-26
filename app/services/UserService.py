from typing import List
from sqlalchemy.orm import Session
from app.schemas import UserSchema
from app.db.models.User import User


def get_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()


def get_by_public_id(db: Session, public_id: str) -> User:
    return db.query(User).filter(User.public_id == public_id).first()


def get_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create(db: Session, user: UserSchema.Create) -> User:
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
