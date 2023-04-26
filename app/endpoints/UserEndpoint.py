from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter

from app.db.session import local_db
from app.schemas import UserSchema
from app.services import UserService

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post('/', response_model=UserSchema.Public)
def create_user(user: UserSchema.Create, db: Session = Depends(local_db)):
    db_user = UserService.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    return UserService.create(db=db, user=user).to_dict()


@router.get('s/', response_model=List[UserSchema.Public])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(local_db)):
    users = UserService.get_all(db, skip=skip, limit=limit)
    return [u.to_dict() for u in users]


@router.get('/{public_id}', response_model=UserSchema.Public)
def get_by_public_id(public_id: str, db: Session = Depends(local_db)):
    db_user = UserService.get_by_public_id(db, public_id=public_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    return db_user.to_dict()
