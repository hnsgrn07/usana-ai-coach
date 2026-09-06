# database.py

# Sets up the connection to our SQLite database file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The database is just a single file sitting in the project folder
DATABASE_URL = "sqlite:///./usana_coach.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Used to open a "conversation" with the database for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our database table classes will inherit from this
Base = declarative_base()