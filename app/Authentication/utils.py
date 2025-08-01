from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt, ExpiredSignatureError
from common import get_secret
from app.models.models import User
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = get_secret("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = get_secret("REFRESH_TOKEN_EXPIRE_MINUTES")
ALGORITHM = get_secret("ALGORITHM")
JWT_SECRET_KEY = get_secret('JWT_SECRET_KEY')   # should be kept secret
JWT_REFRESH_SECRET_KEY = get_secret('JWT_REFRESH_SECRET_KEY')    # should be kept secret

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)



def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def decode_access_token(db:Session ,token:str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        print(subject)
        user = db.query(User).filter(User.email == subject).first()
        if user and user.is_active:
            return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid token")

def custom_user_authentication(token: str = Depends(oauth2_scheme), request: Request = Depends()):
    user = decode_access_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Store user information in the request state
    request.state.user = user

    return user

