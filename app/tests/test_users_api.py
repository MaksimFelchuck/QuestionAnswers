import pytest
from fastapi import status
from app.models.user import UserCreate


class TestUserRegistration:
    """Тесты для регистрации пользователей"""
    
    def test_register_user_success(self, client, test_user_data):
        """Тест успешной регистрации пользователя"""
        response = client.post("/api/v1/users/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Проверяем, что пользователь создался с правильными данными
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        # Пароль не должен возвращаться
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_register_user_duplicate_email(self, client, test_user_data):
        """Тест регистрации с дублирующимся email"""
        # Создаем первого пользователя
        response1 = client.post("/api/v1/users/register", json=test_user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Пытаемся создать второго с тем же email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "different_username"
        response2 = client.post("/api/v1/users/register", json=duplicate_data)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]
    
    def test_register_user_duplicate_username(self, client, test_user_data):
        """Тест регистрации с дублирующимся username"""
        # Создаем первого пользователя
        response1 = client.post("/api/v1/users/register", json=test_user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Пытаемся создать второго с тем же username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response2 = client.post("/api/v1/users/register", json=duplicate_data)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]
    
    def test_register_user_invalid_email(self, client, test_user_data):
        """Тест регистрации с невалидным email"""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/users/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_missing_fields(self, client):
        """Тест регистрации с отсутствующими полями"""
        incomplete_data = {"username": "testuser"}
        
        response = client.post("/api/v1/users/register", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Тесты для авторизации пользователей"""
    
    def test_login_success(self, client, test_user_data):
        """Тест успешной авторизации"""
        # Сначала регистрируем пользователя
        register_response = client.post("/api/v1/users/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Теперь пытаемся войти
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/users/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Проверяем структуру токена
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0
    
    def test_login_invalid_email(self, client, test_user_data):
        """Тест авторизации с неверным email"""
        # Регистрируем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        
        # Пытаемся войти с неверным email
        login_data = {
            "email": "wrong@example.com",
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/users/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client, test_user_data):
        """Тест авторизации с неверным паролем"""
        # Регистрируем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        
        # Пытаемся войти с неверным паролем
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]


class TestUserList:
    """Тесты для получения списка пользователей"""
    
    def test_get_users_empty(self, client):
        """Тест получения пустого списка пользователей"""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
    
    def test_get_users_with_data(self, client, test_user_data, test_user_data2):
        """Тест получения списка пользователей с данными"""
        # Создаем двух пользователей
        client.post("/api/v1/users/register", json=test_user_data)
        client.post("/api/v1/users/register", json=test_user_data2)
        
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data) == 2
        usernames = [user["username"] for user in data]
        assert test_user_data["username"] in usernames
        assert test_user_data2["username"] in usernames
        
        # Проверяем структуру данных пользователя
        user = data[0]
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "is_active" in user
        assert "created_at" in user
        assert "updated_at" in user
        assert "password" not in user
        assert "hashed_password" not in user


class TestUserDetail:
    """Тесты для получения информации о пользователе"""
    
    def test_get_user_by_id_success(self, client, test_user_data):
        """Тест получения пользователя по ID"""
        # Создаем пользователя
        register_response = client.post("/api/v1/users/register", json=test_user_data)
        user_id = register_response.json()["id"]
        
        response = client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == user_id
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
    
    def test_get_user_by_id_not_found(self, client):
        """Тест получения несуществующего пользователя"""
        response = client.get("/api/v1/users/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]


class TestUserUpdate:
    """Тесты для обновления пользователей"""
    
    def test_update_user_success(self, client, test_user_data):
        """Тест успешного обновления пользователя"""
        # Создаем пользователя
        register_response = client.post("/api/v1/users/register", json=test_user_data)
        user_id = register_response.json()["id"]
        
        # Обновляем данные
        update_data = {
            "username": "updated_username",
            "email": "updated@example.com"
        }
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["username"] == update_data["username"]
        assert data["email"] == update_data["email"]
        assert data["id"] == user_id
    
    def test_update_user_not_found(self, client):
        """Тест обновления несуществующего пользователя"""
        update_data = {"username": "new_username"}
        response = client.put("/api/v1/users/999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]
    
    def test_update_user_partial(self, client, test_user_data):
        """Тест частичного обновления пользователя"""
        # Создаем пользователя
        register_response = client.post("/api/v1/users/register", json=test_user_data)
        user_id = register_response.json()["id"]
        
        # Обновляем только username
        update_data = {"username": "partial_update"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["username"] == update_data["username"]
        assert data["email"] == test_user_data["email"]  # Не изменился


class TestUserDelete:
    """Тесты для удаления пользователей"""
    
    def test_delete_user_success(self, client, test_user_data):
        """Тест успешного удаления пользователя"""
        # Создаем пользователя
        register_response = client.post("/api/v1/users/register", json=test_user_data)
        user_id = register_response.json()["id"]
        
        # Удаляем пользователя
        response = client.delete(f"/api/v1/users/{user_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""  # Нет тела ответа
        
        # Проверяем, что пользователь действительно удален
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_user_not_found(self, client):
        """Тест удаления несуществующего пользователя"""
        response = client.delete("/api/v1/users/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]


class TestTokenRefresh:
    """Тесты для обновления токенов"""
    
    def test_refresh_token_success(self, client, test_user_data):
        """Тест успешного обновления токена"""
        # Регистрируем и авторизуем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Обновляем токен
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/users/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        
        # Новый refresh токен должен отличаться от старого
        assert data["refresh_token"] != refresh_token
    
    def test_refresh_token_invalid(self, client):
        """Тест обновления с неверным токеном"""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/api/v1/users/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid refresh token" in response.json()["detail"]


class TestCurrentUser:
    """Тесты для получения информации о текущем пользователе"""
    
    def test_get_current_user_success(self, client, test_user_data):
        """Тест получения информации о текущем пользователе"""
        # Регистрируем и авторизуем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Получаем информацию о текущем пользователе
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "is_active" in data
    
    def test_get_current_user_no_token(self, client):
        """Тест получения информации без токена"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_current_user_invalid_token(self, client):
        """Тест получения информации с неверным токеном"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in response.json()["detail"]


class TestAPIStructure:
    """Тесты структуры API"""
    
    def test_root_endpoint(self, client):
        """Тест корневого endpoint"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Welcome to QuestionAnswers API" in data["message"]
    
    def test_openapi_docs(self, client):
        """Тест доступности OpenAPI документации"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
    
    def test_api_endpoints_structure(self, client):
        """Тест структуры API endpoints"""
        # Проверяем, что все endpoints доступны
        endpoints = [
            ("GET", "/api/v1/users/"),
            ("POST", "/api/v1/users/register"),
            ("POST", "/api/v1/users/login"),
            ("POST", "/api/v1/users/refresh"),
            ("GET", "/api/v1/users/me"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            
            # Должны получить ошибку валидации, но не 404
            assert response.status_code != 404
