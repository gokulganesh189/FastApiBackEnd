from fastapi import FastAPI
from app.Authentication.auth_middleware import JWTAuthenticationMiddleware
from app.routes import views
from pydantic import BaseModel
import uvicorn
import app.routes.views
from app.models.db import Base, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["http://localhost:3000",
           "localhost:3000"]  # Update with your React app's URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(views.router, prefix="/api")
# app.include_router(post.router, prefix="/posts", tags=["posts"])

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.get('/')
def health_check():
    return {"message": "Welcome to Balasundar's Technical Blog"}