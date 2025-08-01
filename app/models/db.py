from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from common import get_secret

SQLALCHEMY_DATABASE_URL = \
    f"mysql+mysqldb://{get_secret('USER')}:{get_secret('PASSWORD')}@{get_secret('HOST')}/{get_secret('NAME')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()