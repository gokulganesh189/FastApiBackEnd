from typing import List
from sqlalchemy.orm import Session
from app.Exceptions.exceptions import UserInfoInfoAlreadyExistError, UserInfoNotFoundError, EmailPasswordError
from app.models.models import User, Post, Image, Caption, Comment
from app.schemas.schemas import CreateAndUpdateUser, UserLogin, UserLoginResponse, PostCreate
from app.Authentication.utils import get_hashed_password, verify_password, create_access_token, create_refresh_token
import uuid
from PIL import Image as ImagePackage
from io import BytesIO

uploads_dir = "/home/equipo/MyProject/FrontEnd/insta-clone-front-end/public/images/uploads"
post_pics_dir = "posts"


# Function to get list of car info
def get_all_user(session: Session, limit: int, offset: int) -> List[User]:
    return session.query(User).offset(offset).limit(limit).all()


# Function to  get info of a particular car
def get_user_info_by_id(session: Session, _id: int) -> User:
    user_info = session.query(User).get(_id)

    if user_info is None:
        raise UserInfoNotFoundError

    return user_info


# Function to add a new car info to the database
def create_user(session: Session, user_info: CreateAndUpdateUser, profile_pic_path: str = None):
    user_details = session.query(User).filter(User.email == user_info.email).first()
    if user_details is not None:
        raise UserInfoInfoAlreadyExistError

    user_info.password = get_hashed_password(user_info.password)
    if profile_pic_path:
        user_info.profile_pic_path = profile_pic_path
    new_user_info = User(**user_info.__dict__)
    session.add(new_user_info)
    session.commit()
    session.refresh(new_user_info)
    return new_user_info


# Function to update details of the car
def update_user_info(session: Session, _id: int, info_update: CreateAndUpdateUser) -> User:
    car_info = get_user_info_by_id(session, _id)

    if car_info is None:
        raise UserInfoNotFoundError

    car_info.username = info_update.username
    car_info.email = info_update.email
    car_info.password = info_update.password

    session.commit()
    session.refresh(car_info)

    return car_info


# Function to delete a car info from the db
def delete_user_info(session: Session, _id: int):
    car_info = get_user_info_by_id(session, _id)

    if car_info is None:
        raise UserInfoNotFoundError

    session.delete(car_info)
    session.commit()

    return


def user_login(session: Session, user_creds: UserLogin):
    user_details = session.query(User).filter(User.email == user_creds.email).first()
    if user_details is None:
        raise UserInfoNotFoundError
    password_db = user_details.password
    if not verify_password(user_creds.password, password_db):
        raise EmailPasswordError

    return {
        "access_token": create_access_token(user_details.email),
        "refresh_token": create_refresh_token(user_details.email),
        "email": user_details.email,
        "user_id": user_details.id
    }


def create_post(db: Session, post_data: PostCreate, post_pic_paths):
    # Create a new post
    user_details = db.query(User).filter(User.id == post_data.user_id).first()
    if user_details is None:
        raise UserInfoNotFoundError
    new_post = Post(user_id=post_data.user_id)

    # Create a caption for the post (even if there's only one)
    captions = None
    if post_data.caption is not None:
        captions = Caption(description=post_data.caption)
        new_post.caption.append(captions)
        print(post_data.caption)
        print()
    print(post_pic_paths[0].size)
    if post_pic_paths[0].size > 0:
        allowed_formats = ["png", "jpeg", "jpg"]
        for image_path in post_pic_paths:
            file_extension = image_path.filename.split(".")[-1].lower()
            if file_extension in allowed_formats:
                unique_filename = str(uuid.uuid4())
                # file_extension = image_path.filename.split(".")[-1]
                new_filename = f"{unique_filename}.{file_extension}"
                image = ImagePackage.open(BytesIO(image_path.file.read()))
                # image = image.resize((400, 400), ImagePackage.LANCZOS)
                image_url = f"{uploads_dir}/{post_pics_dir}/{new_filename}"
                image.save(image_url, "jpeg")
                image = Image(image_url=image_url)
                new_post.images.append(image)
            else:
                return {"details":f"Not supported image format we support {allowed_formats}"}

    # Add the caption to the post (this is not needed due to the relationship)
    # Commit the changes to the database
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "post_id": new_post.id,
        "user_id": new_post.user_id,
        "caption": captions.description if captions else None,  # You can access the description directly
        "images": [img.image_url for img in new_post.images]
    }


def listposts(session: Session, limit: int, offset: int, user_id: int):
    # return session.query(Post).filter(Post.user_id == user_id).offset(offset).limit(limit).all()
    query = (
        session.query(Post)
        .outerjoin(Caption, Post.id == Caption.post_id)
        .outerjoin(Image, Post.id == Image.post_id)
        .filter(Post.user_id == user_id)
        # .offset(offset)
        # .limit(limit)
        .all()
    )

    # Create a list to store the posts along with their captions and images
    posts_with_details = []

    for post in query:
        captions = [caption.description for caption in post.caption]
        images = [{'image_url': image.image_url, 'image_like': image.image_like} for image in post.images]

        # Create a dictionary for the post with additional details
        post_data = {
            'post_id': post.id,
            'user_id': post.user_id,
            'created_on': post.created_on,
            'is_caption': post.is_caption,
            'post_black_marks': post.post_black_marks,
            'is_image': post.is_image,
            'captions': captions,
            'images': images
        }

        posts_with_details.append(post_data)

    return posts_with_details