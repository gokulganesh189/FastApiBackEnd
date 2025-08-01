from pydantic import BaseModel, ValidationError
from typing import Optional, List
from fastapi import UploadFile, Form, File


class CreateAndUpdateUser(BaseModel):
    username: str
    email: str
    password: str
    name: Optional[str]=None
    user_theme: Optional[str]=None
    profile_pic_path: Optional[str]=None


try:
    CreateAndUpdateUser.model_validate({
        "id": 23,
        "username": "testNew1234",
        "email": "testemail134@gmail.com",
        "password": "string",
        "name": "Gokul",
        "user_theme": "dark",
        "two_fa_enabled": False,
        "profile_pic_path": "profile_pic.jpg",
    })
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))


class User(CreateAndUpdateUser):
    id: int

    class Config:
        from_attributes = True


class PaginatedUserInfo(BaseModel):
    limit: int
    offset: int
    data: List[User]


class UserLogin(BaseModel):
    email: str
    password: Optional[str]


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    email: str
    user_id:int


class PostCreate(BaseModel):
    user_id: int
    caption: Optional[str]=None
    post_pic_paths:Optional[str]=None


class ListPosts(BaseModel):
    limit: int
    offset: int
    data: List[PostCreate]


class PostResponse(BaseModel):
    post_id: int
    user_id: int
    caption: list[str]
    images: list[str]
