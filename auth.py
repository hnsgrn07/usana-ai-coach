# auth.py
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()  # Load environment variables from .env file


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-this")  # Use a default value for development
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expiration time in minutes
# Turns a plain password into a secure hash before saving it
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


# Checks a plain password against the stored hash during login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Builds a signed token that proves who logged in, expiring after an hour
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Reads a token back and returns its contents, or None if it's invalid/expired
def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None