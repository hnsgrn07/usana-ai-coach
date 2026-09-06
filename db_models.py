# db_models.py

# Describes the "profiles" table in the database
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from database import Base
from datetime import datetime


class ProfileDB(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    full_name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    weight_kg = Column(Float)
    height_cm = Column(Float)
    activity_level = Column(String)
    health_goals = Column(JSON)            # stored as a list, e.g. ["energy_support"]
    dietary_restrictions = Column(JSON)
    notes = Column(String, nullable=True)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)