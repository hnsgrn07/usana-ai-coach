# db_models.py

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, Date, UniqueConstraint
from datetime import datetime
from database import Base


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
    health_goals = Column(JSON)
    dietary_restrictions = Column(JSON)
    notes = Column(String, nullable=True)
    coaching_text = Column(String, nullable=True)
    coaching_generated_at = Column(DateTime, nullable=True)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    sponsor_id = Column(String, nullable=True)   # links to whoever's token they registered with
    created_at = Column(DateTime, default=datetime.utcnow)


# One-time-use token that a QR code encodes — validates a new member's registration
class EnrollmentToken(Base):
    __tablename__ = "enrollment_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    sponsor_id = Column(String, nullable=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Tracks whether a member checked in as having taken their supplements
# on a given day — one row per user per date
class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    log_date = Column(Date)
    completed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # A user can only have one check-in per calendar day
    __table_args__ = (UniqueConstraint("user_id", "log_date", name="unique_user_date"),)

# Records a dated snapshot every time a profile is saved/updated,
# so we can show progress over time instead of only the latest state
class ProfileSnapshot(Base):
    __tablename__ = "profile_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    snapshot_date = Column(Date)
    weight_kg = Column(Float)
    health_goals = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)