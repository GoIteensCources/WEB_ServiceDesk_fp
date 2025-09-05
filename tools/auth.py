import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from models.models import User
from settings import api_config, async_session
from fastapi import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"Authorization": "Bearer"},
)

# openssl rand -hex 32
def generate_secret_key():
    return os.urandom(32).hex()


def create_access_token(payload: dict, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=api_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload.update({"exp": expire})
    print(payload)
    jwt_token = jwt.encode(
        payload, api_config.SECRET_KEY, algorithm=api_config.ALGORITHM
    )
    return jwt_token


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            api_config.SECRET_KEY,
            algorithms=[api_config.ALGORITHM],
            options={"verify_exp": False},
        )

        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        print({"error": "Token has expired"})
        return False
    except jwt.InvalidTokenError as e:
        print({"error": f"Invalid token: {e}"})
        return False


async def authenticate_user(username: str, password: str):
    async with async_session() as session:
        user_stmt = select(User).where(User.username == username)
        user = await session.execute(user_stmt)
        user = user.scalar_one_or_none()

        if not user:
            return False
        if not check_password_hash(user.password, password):
            return False
        return user


async def get_user_by_id(user_id: Optional[int]) -> Optional[User]:
    async with async_session() as session:
        user_stmt = select(User).where(User.id == user_id)
        user = await session.execute(user_stmt)
        return user.scalar_one_or_none()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_token = decode_access_token(token)
    if not user_token:
        raise credentials_exception
    user = await get_user_by_id(user_id = int(user_token.get("sub")))

    return user


def require_admin(user: dict = Depends(get_current_user)):
    if not user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    return user
