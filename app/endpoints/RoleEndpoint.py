from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter

from app.db.session import local_db
from app.schemas import RoleSchema
from app.services import RoleService, UserService

router = APIRouter(
    prefix="/role",
    tags=["role"],
    responses={404: {"description": "Not found"}},
)


@router.post('/', response_model=RoleSchema.Public)
def create_role(role: RoleSchema.Create, db: Session = Depends(local_db)):
    db_role = RoleService.get_by_name(db, role.name)
    if db_role:
        raise HTTPException(status_code=400, detail="Email already registered.")

    return RoleService.create(db=db, role=role).to_dict()


@router.get('s/', response_model=List[RoleSchema.Public])
def get_all_roles(skip: int = 0, limit: int = 100, db: Session = Depends(local_db)):
    roles = RoleService.get_all(db, skip=skip, limit=limit)
    return [r.to_dict() for r in roles]


@router.get('/{public_id}', response_model=RoleSchema.Public)
def get_by_public_id(public_id: str, db: Session = Depends(local_db)):
    db_role = RoleService.get_by_public_id(db, public_id=public_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found.")

    return db_role.to_dict()


@router.post('/{public_role_id}/user/{public_user_id}', response_model=RoleSchema.Public)
def assign_role_to_user(public_role_id: str, public_user_id: str, db: Session = Depends(local_db)):
    db_role = RoleService.get_by_public_id(db, public_id=public_role_id)
    db_user = UserService.get_by_public_id(db, public_id=public_user_id)
    if not db_role or not db_user:
        entity = "Role" if not db_role else "User"
        raise HTTPException(status_code=404, detail=f"{entity} not found.")
    RoleService.add_role_to_user(db, db_role, db_user)
    return db_role.to_dict()
