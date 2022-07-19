from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import constants as cons

DB_URL = cons.DB_URL
engine = create_engine(DB_URL, connect_args={}, future=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()