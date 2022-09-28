from pydantic import BaseModel

class UserBase(BaseModel):
    email:str

class RegistrationSchema(UserBase):
    password: str