from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.db import Base

# Association table for followers
followers_table = Table('followers', Base.metadata,
                        Column('follower_id', Integer, ForeignKey('users.id')),
                        Column('followed_id', Integer, ForeignKey('users.id'))
                        )

# Association table for posts and hashtags (many-to-many)
post_hashtags = Table('post_hashtags', Base.metadata,
                      Column('post_id', Integer, ForeignKey('posts.id')),
                      Column('hashtag_id', Integer, ForeignKey('hashtags.id'))
                      )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(255), unique=True)
    password = Column(String(255))
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    two_fa_enabled = Column(Boolean, default=False, nullable=True)
    black_marks = Column(Integer)
    profile_pic_path = Column(String(255), default=None, nullable=True)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

    # Add fields for additional user profile details, privacy settings, etc.

    # Relationships
    posts = relationship("Post", back_populates="user")
    likes = relationship("Like", back_populates="user_likes")
    followers = relationship("User", secondary=followers_table,
                             primaryjoin=(followers_table.c.follower_id == id),
                             secondaryjoin=(followers_table.c.followed_id == id),
                             backref="followed_by"
                             )
    user_theme = Column(String(50), nullable=True)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_on = Column(DateTime, server_default=func.now())
    post_black_marks = Column(Integer, nullable=True)
    is_caption = Column(Boolean, default=False, nullable=True)
    is_image = Column(Boolean, default=False, nullable=True)
    # Add fields for shared posts, save/favorites, etc.

    # Relationships
    caption = relationship("Caption", back_populates="posts")
    user = relationship("User", back_populates="posts")
    images = relationship("Image", back_populates="post")
    comments = relationship("Comment", back_populates="posts")
    hashtags = relationship("Hashtag", secondary=post_hashtags, back_populates="posts")

class Caption(Base):
    __tablename__ = "captions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    description = Column(Text, nullable=True)
    # Define the relationship between Caption and Post
    posts = relationship("Post", back_populates="caption")

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    image_url = Column(String(255), nullable=True)
    image_like = Column(Integer)

    # Add fields for image details

    # Relationships
    post = relationship("Post", back_populates="images")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comment = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_on = Column(DateTime, server_default=func.now())
    has_reply = Column(Boolean, default=False)
    comment_likes = Column(Integer)

    # Add fields for replies, reports/flagging, etc.

    # Relationships
    posts = relationship("Post", back_populates="comments")
    replies = relationship("CommentReplies", back_populates="comment")


class CommentReplies(Base):
    __tablename__ = "comments_replys"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comment = Column(Text)
    comment_reply_likes = Column(Integer)
    comment_id = Column(Integer, ForeignKey("comments.id"))

    # Relationships
    comment = relationship("Comment", back_populates="replies")

class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    like = Column(Integer)
    user_id = Column(Integer,ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"))
    comment_reply_id = Column(Integer, ForeignKey("comments_replys.id"))
    user_likes = relationship("User", back_populates="likes")

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True)

    # Relationships
    posts = relationship("Post", secondary=post_hashtags, back_populates="hashtags")
