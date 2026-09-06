# auth.py

# Handles turning plain passwords into secure hashes, and checking them later
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Turns a plain password into a secure hash before saving it
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


# Checks a plain password against the stored hash during login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)