import pytest
from datetime import timedelta
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash
)


class TestAuthService:
    def test_create_access_token_success(self):
        """Тест успешного создания access токена"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Проверяем, что токен можно декодировать напрямую
        from jose import jwt
        from app.core.config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_with_expires_delta(self):
        """Тест создания access токена с кастомным временем жизни"""
        data = {"sub": "test@example.com", "user_id": 1}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        
        # Проверяем payload
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "jti" in payload  # Проверяем наличие случайного ID

    def test_create_refresh_token_success(self):
        """Тест успешного создания refresh токена"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Проверяем, что токен можно декодировать
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_refresh_token_expiration(self):
        """Тест времени жизни refresh токена"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_refresh_token(data)
        
        payload = verify_token(token)
        assert "exp" in payload
        assert "jti" in payload  # Проверяем наличие случайного ID
        assert payload["type"] == "refresh"

    def test_verify_token_success(self):
        """Тест успешной верификации токена"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["type"] == "access"

    def test_verify_token_invalid(self):
        """Тест верификации неверного токена"""
        payload = verify_token("invalid_token")
        assert payload is None

    def test_verify_token_empty(self):
        """Тест верификации пустого токена"""
        payload = verify_token("")
        assert payload is None

    def test_verify_token_none(self):
        """Тест верификации None токена"""
        with pytest.raises(AttributeError):
            verify_token(None)

    def test_token_payload_structure(self):
        """Тест структуры payload токена"""
        data = {"sub": "test@example.com", "user_id": 1, "custom_field": "value"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["custom_field"] == "value"
        assert payload["type"] == "access"
        assert "exp" in payload
        # iat может отсутствовать в некоторых версиях python-jose

    def test_access_token_default_expiration(self):
        """Тест времени жизни access токена по умолчанию"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)  # Без expires_delta
        
        payload = verify_token(token)
        assert "exp" in payload
        assert "jti" in payload  # Проверяем наличие случайного ID
        assert payload["type"] == "access"

    def test_token_uniqueness(self):
        """Тест уникальности токенов"""
        data = {"sub": "test@example.com", "user_id": 1}
        
        token1 = create_access_token(data)
        token2 = create_access_token(data)
        
        # Токены должны быть разными из-за случайного jti
        assert token1 != token2

    def test_refresh_token_uniqueness(self):
        """Тест уникальности refresh токенов"""
        data = {"sub": "test@example.com", "user_id": 1}
        
        token1 = create_refresh_token(data)
        token2 = create_refresh_token(data)
        
        # Токены должны быть разными из-за случайного jti
        assert token1 != token2

    def test_token_with_complex_data(self):
        """Тест токена со сложными данными"""
        complex_data = {
            "sub": "test@example.com",
            "user_id": 1,
            "roles": ["admin", "user"],
            "permissions": {"read": True, "write": False},
            "metadata": {"created_by": "system", "version": "1.0"}
        }
        
        token = create_access_token(complex_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == complex_data["sub"]
        assert payload["user_id"] == complex_data["user_id"]
        assert payload["roles"] == complex_data["roles"]
        assert payload["permissions"] == complex_data["permissions"]
        assert payload["metadata"] == complex_data["metadata"]

    def test_token_expiration_handling(self):
        """Тест обработки истекших токенов"""
        # Создаем токен с очень коротким временем жизни
        data = {"sub": "test@example.com", "user_id": 1}
        expires_delta = timedelta(seconds=1)
        token = create_access_token(data, expires_delta)
        
        # Сразу проверяем - должен быть валидным
        payload = verify_token(token)
        assert payload is not None
        
        # Ждем истечения токена
        import time
        time.sleep(2)
        
        # Теперь токен должен быть невалидным
        payload = verify_token(token)
        assert payload is None

    def test_password_verification(self):
        """Тест верификации паролей"""
        password = "securepassword456"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password(password + "extra", hashed) is False
        assert verify_password("", hashed) is False
        
        # Проверяем, что неверный хеш вызывает исключение
        from passlib.exc import UnknownHashError
        with pytest.raises(UnknownHashError):
            verify_password(password, "invalid_hash")
