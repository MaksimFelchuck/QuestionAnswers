from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings
from app.core.logging import auth_logger
import random

# Настройка для хеширования паролей
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    auth_logger.debug("Verifying password")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    auth_logger.debug("Hashing password")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание access токена"""
    auth_logger.debug("Creating access token")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access", "jti": str(random.randint(1000, 9999))})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    auth_logger.info("Access token created successfully")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание refresh токена"""
    auth_logger.debug("Creating refresh token")
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(random.randint(1000, 9999))})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    auth_logger.info("Refresh token created successfully")
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Проверка токена"""
    auth_logger.debug("Verifying token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        auth_logger.debug("Token verified successfully")
        return payload
    except JWTError as e:
        auth_logger.warning(f"Token verification failed: {str(e)}")
        return None
