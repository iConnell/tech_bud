from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.users import RegistrationSchema
from ..models.users import User
from .utils import hash_password, create_access_token, verify_password


router = APIRouter(prefix='/api/auth')


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