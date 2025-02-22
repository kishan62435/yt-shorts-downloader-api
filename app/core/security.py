from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
# from app.core.config import SECRET_KEY, ALGORITHM
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        print("expires_delta", expires_delta)
        expire = datetime.utcnow() + expires_delta
    else:
        print("ACCESS_TOKEN_EXPIRE_MINUTES", ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + timedelta(minutes=720)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None