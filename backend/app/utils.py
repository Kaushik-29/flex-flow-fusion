<<<<<<< HEAD
import os
from datetime import datetime, timedelta
import jwt as pyjwt
import bcrypt

SECRET_KEY = os.getenv("JWT_SECRET", "flex-it-out-super-secret-jwt-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

_BCRYPT_ROUNDS = 12


def _normalize_password(password: str) -> bytes:
    return password.encode("utf-8")[:72]

def hash_password(password: str) -> str:
    password_bytes = _normalize_password(password)
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_normalize_password(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False
=======
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt as pyjwt

SECRET_KEY = "your_jwt_secret_key"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
>>>>>>> 73104143b6642647d1cbb806129d6444f6ec9d2f

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except pyjwt.PyJWTError:
        return None