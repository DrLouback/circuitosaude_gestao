from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL) #type: ignore
conn = engine.connect()

SessionLocal = sessionmaker(engine)

def get_session():
    return SessionLocal()

class Base(DeclarativeBase):
    pass


