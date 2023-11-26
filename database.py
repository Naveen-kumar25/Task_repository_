from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:Naveen25\@localhost:5432/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL)

Session = sessionmaker(bind=engine,autocommit=False)

Base = declarative_base()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

