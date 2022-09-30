from pydantic import BaseModel
from .users import UserBase, ReadOtherUser

class PostBaseSchema(BaseModel):
    id: int

class PostCreateSchema(BaseModel):
    title: str
    body: str

class PostReadSchema(PostBaseSchema):
    title: str
    body: str
    post_author: UserBase

    class Config:
        orm_mode = True
