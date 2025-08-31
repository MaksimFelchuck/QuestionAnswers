from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings
import random


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создать access токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    
    # Добавляем случайное значение для уникальности токенов (jti должен быть строкой)
    to_encode.update({"exp": expire, "type": "access", "jti": str(random.randint(1000, 9999))})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict):
    """Создать refresh токен"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=30)  # Refresh токен живет 30 дней
    # Добавляем случайное значение для уникальности токенов (jti должен быть строкой)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(random.randint(1000, 9999))})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str):
    """Проверить токен"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
