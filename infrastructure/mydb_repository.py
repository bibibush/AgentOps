import os
from domain.ports import MyDBPort
from infrastructure.db import get_engine, get_session_factory

class MyDBRepository(MyDBPort):
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")
        engine = get_engine(database_url)
        session_factory = get_session_factory(engine)
        self.session = session_factory()