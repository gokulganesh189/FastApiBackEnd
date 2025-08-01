import traceback

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.models.crud import create_user, get_all_user, user_login, create_post, listposts
from app.models.db import get_db
from app.models.models import User as UserDb
from app.Exceptions.exceptions import *
from app.schemas.schemas import *
from app.Authentication.utils import decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from common import get_secret
from jose import jwt
import os
import shutil
import uuid
from PIL import Image
from io import BytesIO

router = APIRouter()

ALGORITHM = "HS256"
JWT_SECRET_KEY = get_secret('JWT_SECRET_KEY')

# class User:
#     def __init__(self, session: Session = Depends(get_db)):
#         self.session = session
#
#     @router.get("/list/users", response_model=PaginatedUserInfo)
#     def list_users(self, limit:int=10, offset:int=0):
#         user_list = get_all_user(self.session, limit, offset)
#         response = {"limit": limit, "offset": offset, "data": user_list}
#
#         return response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define the directory names
uploads_dir = "/home/equipo/MyProject/FrontEnd/insta-clone-front-end/public/images/uploads"
profile_pics_dir = "profile_pics"


# Function to create directories if they don't exist
def create_directories_if_not_exist():
    if not os.path.exists(uploads_dir):
        os.mkdir(uploads_dir)
    profile_pics_path = os.path.join(uploads_dir, profile_pics_dir)
    if not os.path.exists(profile_pics_path):
        os.mkdir(profile_pics_path)


create_directories_if_not_exist()


@router.post("/signup", response_model=CreateAndUpdateUser)
async def signup(
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        name: str = Form(None),
        user_theme: str = Form(None),
        two_fa_enabled: str = Form(None),
        profile_pic: UploadFile = File(None),
        db: Session = Depends(get_db)):
    try:
        # Validate the user input
        if not username or not email or not password:
            raise HTTPException(status_code=400, detail="Username, email, password, and additional_info are required.")

        # Save the user's data (you can add database integration here)
        user_data = CreateAndUpdateUser(
            username=username,
            email=email,
            password=password,
            name=name,
            user_theme=user_theme,
            two_fa_enabled=two_fa_enabled
        )

        # Save the profile picture if provided
        profile_pic_path = None
        if profile_pic and profile_pic.size>0:
            unique_filename = str(uuid.uuid4())
            file_extension = profile_pic.filename.split(".")[-1]
            new_filename = f"{unique_filename}.{file_extension}"

            image = Image.open(BytesIO(profile_pic.file.read()))
            # crop_box = (0, 0, 800, 800)
            image = image.resize((400, 400),Image.LANCZOS)

            profile_pic_path = f"{uploads_dir}/{profile_pics_dir}/{new_filename}"
            image.save(profile_pic_path, "JPEG")

        db_user = create_user(session=db, user_info=user_data, profile_pic_path=profile_pic_path)
        return db_user
    except UserInfoInfoAlreadyExistError as err:
        raise HTTPException(status_code=err.status_code, detail=err.show_message_exists())


@router.get("/list/users", response_model=PaginatedUserInfo)
async def list_all_users(limit: int = 10, offset: int = 0, db: Session = Depends(get_db),
                         token: str = Depends(oauth2_scheme)):
    # Verify the access token here.
    try:
        user = decode_access_token(db, token)
        if user is not None:
            user_list = get_all_user(db, limit, offset)
            response = {"limit": limit, "offset": offset, "data": user_list}
            return response
        else:
            raise UserInfoNotFoundError()
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except UserInfoNotFoundError as err:
        # Handle the UserInfoNotFoundError and return its detail
        raise HTTPException(status_code=err.status_code, detail=err.detail)


@router.post("/login", response_model=UserLoginResponse)
def login(user_loggin: UserLogin, db: Session = Depends(get_db)):
    try:
        response = user_login(session=db, user_creds=user_loggin)
        return response
    except EmailPasswordError as err:
        raise HTTPException(status_code=err.status_code, detail=err.check_username_password())
    except UserInfoNotFoundError as err:
        raise HTTPException(status_code=err.status_code, detail=err.show_message_not_found())


@router.post("/uploader/")
async def create_upload_file(profile_pic: UploadFile = File(...)):
    if profile_pic:
        profile_pic_path = f"{uploads_dir}/{profile_pics_dir}/{profile_pic.filename}"
        with open(profile_pic_path, "wb") as f:
            f.write(profile_pic.file.read())
        return {"filename": profile_pic.filename}


@router.post("/create/post")
async def create_new_post(
        user_id: int = Form(...),
        caption: str = Form(None),
        post_pic_paths: List[UploadFile] = File(None),
        db: Session = Depends(get_db),
        # token: str = Depends(oauth2_scheme)
):
    try:
        # user = decode_access_token(db, token)
        # if user is None:
        #     raise HTTPException(status_code=400, detail="user info is required")
        post_data = PostCreate(
            user_id=user_id,
            caption=caption
        )
        # image_paths = [f"{uploads_dir}/{profile_pics_dir}/{image.filename}" for image in post_pic_paths]
        # print(image_paths)
        new_post = create_post(db=db, post_data=post_data, post_pic_paths=post_pic_paths)
        return new_post
    except UserInfoInfoAlreadyExistError as err:
        raise HTTPException(status_code=err.status_code, detail=err.show_message_exists())
    except UserInfoNotFoundError as err:
        raise HTTPException(status_code=err.status_code, detail=err.show_message_not_found())


@router.get("/posts/{user_id}")
def list_all_posts(user_id: int,
                   request: Request,
                   limit: int = 10,
                   offset: int = 0,
                   db: Session = Depends(get_db),
                    token: str = Depends(oauth2_scheme)
                   ):
    try:
        user = decode_access_token(db, token)
        if user is None:
            raise HTTPException(status_code=400, detail="user info is required")
        if user.id == user_id:
            posts = listposts(db, limit, offset, user_id)
            response = {"limit": limit, "user Id":user_id, "offset": offset, "data": [post for post in posts]}
            return response
        else:
            raise HTTPException(status_code=400, detail="Token is not valid")
    except UserInfoInfoAlreadyExistError as err:
        raise HTTPException(status_code=err.status_code, detail=err.show_message_exists())
    except UserInfoNotFoundError as err:
        raise HTTPException(status_code=err.status_code, detail=err.show_message_not_found())
