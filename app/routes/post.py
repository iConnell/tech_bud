from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .auth import get_current_user
from ..models.posts import Post
from ..schemas.users import ReadUser
from ..schemas.post import PostCreateSchema, PostReadSchema


router = APIRouter(
    prefix='/api/posts',
    tags=['Posts']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=PostReadSchema)
def create_post(request: PostCreateSchema, user: ReadUser = Depends(get_current_user), db: Session = Depends(get_db)):
    new_post = Post(**request.dict(), author=user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get('', status_code=status.HTTP_200_OK, response_model=List[PostReadSchema], dependencies=[Depends(get_current_user)])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts

@router.get('/{post_id}', status_code=status.HTTP_200_OK, response_model=PostReadSchema, dependencies=[Depends(get_current_user)])
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail=f"post with id {post_id} not found")

    return post