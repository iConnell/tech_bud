from datetime import timedelta
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.users import RegistrationSchema, UserBase
from ..models.users import User
from .utils import hash_password, create_access_token, verify_password, verify_access_token, sendEmail


router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication']
    )


@router.post('')
def create_user(request: RegistrationSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==request.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email {request.email} already exist")
    
    hashed_password = hash_password(request.password)
    new_user = User(email=request.email, password=hashed_password)

    token = create_access_token({"email": new_user.email})

    #sendEmail(new_user.email, token)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"token":create_access_token({"email": new_user.email, "id":new_user.id})}


@router.post('/login', status_code=status.HTTP_200_OK)
def user_login(request: RegistrationSchema, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.email==request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials provied")
    
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials provied")

    return {"token":create_access_token({"email": user.email, "id":user.id})}


@router.post('/verify-email/{token}', status_code=status.HTTP_200_OK)
def verify_email(token, db: Session = Depends(get_db)):
    payload = verify_access_token(token)

    new_user = db.query(User).filter(User.email==payload['email'])

    if not new_user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    new_user.update({"is_active":True})
    db.commit()
    return {}


@router.post('/password/reset', status_code=status.HTTP_200_OK)
def reset_password(request: UserBase, db:Session = Depends(get_db)):    
    user = db.query(User).filter(User.email==request.email).first()
    
    # Todo:
    # Add Logic for sms verification
    try:
        token = create_access_token({"email": user.email, "id":user.id}, timedelta(minutes=10))
        sendEmail(user.email, token)

    except:
        pass

    return {"data": "Email will be sent, if specified email is valid"}