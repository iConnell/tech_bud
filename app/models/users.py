from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Boolean, Integer, DateTime, Table
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from ..database import Base

user_following = Table(
    'user_following', Base.metadata,
    Column('followers', Integer, ForeignKey('users.id'), primary_key=True),
    Column('following', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String, nullable=True,)
    last_name = Column(String, nullable=True,)
    phone = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=False, nullable=True)
    date_joined = Column(DateTime(timezone=True), default=datetime.utcnow())

    following = relationship("User",
        secondary=user_following,
        primaryjoin=id==user_following.c.followers,
        secondaryjoin=id==user_following.c.following,
        backref="followers"
        )
    
    posts = relationship("Post", back_populates="post_author")