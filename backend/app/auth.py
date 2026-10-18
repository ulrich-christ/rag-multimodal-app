from pwdlib import PasswordHash
import jwt
from datetime import datetime, timezone, timedelta
from app.config import ACCESS_TOKEN_EXPIRES_MINUTES, SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.database import get_session
from app.models import User
password_hash = PasswordHash.recommended()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")
def hash_password(password:str)->str:
    return password_hash.hash(password)

def verify_password(password:str, hashed:str)->bool:
    return password_hash.verify(password,hashed)

def create_access_token(user_id:int)->str:
    payload = {
        "sub": str(user_id),
        "exp":datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    }
    return jwt.encode(payload,SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
        token:str = Depends(oauth2_schema),
        session:Session = Depends(get_session),
)-> User:
    credentials_error = HTTPException(
        status_code=401,
        detail="Could not Validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])

        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_error

    user = session.get(User, user_id)
    if user is None:
        raise credentials_error
    return user