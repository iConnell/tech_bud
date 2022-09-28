from pydantic import BaseModel

class UserBase(BaseModel):
    email:str


class RegistrationSchema(UserBase):
    password: str


class ChangePasswordSchema(BaseModel):
    password1:str
    password2:str


class ReadUser(UserBase):
    id: int
    username: str | None = None
    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_active: bool
    gender: str | None = None
    
    class Config:
        orm_mode = True