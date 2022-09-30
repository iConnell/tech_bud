from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from ..schemas.users import ReadUser, ReadOtherUser
from .auth import get_current_user, get_user
from ..database import get_db


router = APIRouter(
    prefix='/api/profile',
    tags=['Users']
)


@router.get('', response_model=ReadUser, status_code=status.HTTP_200_OK)
def get_user_profile(user:ReadUser = Depends(get_current_user)):
    return user

@router.get('/{user_id}', response_model=ReadOtherUser, dependencies=[Depends(get_current_user)])
def get_other_users_profile(user_id: int, db:Session = Depends(get_db)):
    other_user = get_user(user_id, db)

    return other_user

@router.post('/{user_id}/follow', response_model=ReadOtherUser, status_code=status.HTTP_200_OK)
def follow_user(user_id: int, user:ReadUser = Depends(get_current_user), db:Session = Depends(get_db)):

    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot follow yourself")

    other_user = get_user(user_id, db)
    other_user.followers.append(user)
    db.commit()

    return other_user