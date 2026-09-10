# database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Reads the real database location from the environment instead of hardcoding it
DATABASE_URL = os.getenv("DATABASE_URL")

# Postgres doesn't need the SQLite-specific connect_args setting
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()