from email.policy import default
from ..database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
    author = Column(Integer, ForeignKey('users.id'))

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow())

    post_author = relationship("User", back_populates="posts")