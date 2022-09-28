from fastapi import FastAPI
from .routes import auth
from .database import engine
from .models import users


users.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
