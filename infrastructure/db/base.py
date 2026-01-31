from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def get_engine(database_url: str):
    return create_engine(database_url)


def get_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
