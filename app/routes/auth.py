from datetime import timedelta
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db
from ..schemas.users import RegistrationSchema, UserBase, ChangePasswordSchema, ReadUser
from ..models.users import User
from .utils import hash_password, create_access_token, verify_password, verify_access_token, sendEmail


router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication']
    )

oauth2_scheme = OAuth2PasswordBearer('api/auth/login')

def get_user(id:int, db: Session):
    user = db.query(User).filter(User.id==id).first()
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_access_token(token)
        
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        
        user = get_user(id, db)
        if user is None:
            raise credentials_exception
            
        return user
        
    except:
        raise credentials_exception


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

    user = db.query(User).filter(User.email==payload['email'])

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    user.update({"is_active":True})
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


@router.post('/password/change', status_code=status.HTTP_200_OK)
def change_password(passwords:ChangePasswordSchema, user: ReadUser = Depends(get_current_user), db:Session=Depends(get_db)):
    if passwords.password1 != passwords.password2:
        raise HTTPException(status_code=400, detail="passwords do not match")

    hashed_password = hash_password(passwords.password1)
    
    db.query(User).filter(User.id==user.id).update({"password": hashed_password})
    db.commit()

    return {}