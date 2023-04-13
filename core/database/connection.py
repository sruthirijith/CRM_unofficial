from functools import lru_cache
from pymongo import MongoClient

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.base import settings

metadata = sqlalchemy.MetaData()


@lru_cache()
def get_settings():
    return settings()



engine = create_engine(settings.DB_URL)

metadata.create_all(engine)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    print("create_tables")
    Base.metadata.create_all(bind=engine)

def get_mongo_db():
    mongo_client = MongoClient(settings.MONGO_CONN_STR)
    mongo_db_name = settings.MONGO_DB_NAME
    mongo_db = mongo_client[mongo_db_name]
    try:
        yield mongo_db
    finally:
        mongo_client.close()