import pytest
from app.services.user_service import UserService
from app.models.user import UserCreate, UserUpdate
from app.alembic.models.user import User


class TestUserService:
    """Тесты для UserService"""
    
    def test_create_user_success(self, user_service, test_user_data):
        """Тест успешного создания пользователя"""
        user_data = UserCreate(**test_user_data)
        user = user_service.create_user(user_data)
        
        assert user is not None
        assert user.username == test_user_data["username"]
        assert user.email == test_user_data["email"]
        assert user.is_active is True
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None
        # Пароль должен быть захеширован
        assert user.hashed_password != test_user_data["password"]
        assert user.hashed_password.startswith("$2b$")
    
    def test_create_user_duplicate_email(self, user_service, test_user_data):
        """Тест создания пользователя с дублирующимся email"""
        user_data = UserCreate(**test_user_data)
        
        # Создаем первого пользователя
        user1 = user_service.create_user(user_data)
        assert user1 is not None
        
        # Пытаемся создать второго с тем же email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "different_username"
        user_data2 = UserCreate(**duplicate_data)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(user_data2)
        
        assert exc_info.value.status_code == 409
        assert "already exists" in str(exc_info.value.detail)
    
    def test_get_user_by_id_success(self, user_service, test_user_data):
        """Тест получения пользователя по ID"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        
        retrieved_user = user_service.get_user_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == created_user.username
        assert retrieved_user.email == created_user.email
    
    def test_get_user_by_id_not_found(self, user_service):
        """Тест получения несуществующего пользователя по ID"""
        user = user_service.get_user_by_id(999)
        assert user is None
    
    def test_get_user_by_email_success(self, user_service, test_user_data):
        """Тест получения пользователя по email"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        
        retrieved_user = user_service.get_user_by_email(created_user.email)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    def test_get_user_by_email_not_found(self, user_service):
        """Тест получения несуществующего пользователя по email"""
        user = user_service.get_user_by_email("nonexistent@example.com")
        assert user is None
    
    def test_get_all_users_empty(self, user_service):
        """Тест получения пустого списка пользователей"""
        users = user_service.get_all_users()
        assert users == []
    
    def test_get_all_users_with_data(self, user_service, test_user_data, test_user_data2):
        """Тест получения списка пользователей с данными"""
        # Создаем двух пользователей
        user_data1 = UserCreate(**test_user_data)
        user_data2 = UserCreate(**test_user_data2)
        
        user1 = user_service.create_user(user_data1)
        user2 = user_service.create_user(user_data2)
        
        users = user_service.get_all_users()
        
        assert len(users) == 2
        user_ids = [user.id for user in users]
        assert user1.id in user_ids
        assert user2.id in user_ids
    
    def test_update_user_success(self, user_service, test_user_data):
        """Тест успешного обновления пользователя"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        
        update_data = UserUpdate(username="updated_username", email="updated@example.com")
        updated_user = user_service.update_user(created_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.id == created_user.id
        assert updated_user.username == "updated_username"
        assert updated_user.email == "updated@example.com"
        assert updated_user.is_active == created_user.is_active
    
    def test_update_user_partial(self, user_service, test_user_data):
        """Тест частичного обновления пользователя"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        
        # Обновляем только username
        update_data = UserUpdate(username="partial_update")
        updated_user = user_service.update_user(created_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.username == "partial_update"
        assert updated_user.email == created_user.email  # Не изменился
    
    def test_update_user_password(self, user_service, test_user_data):
        """Тест обновления пароля пользователя"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        old_password_hash = created_user.hashed_password
        
        update_data = UserUpdate(password="newpassword123")
        updated_user = user_service.update_user(created_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.hashed_password != old_password_hash
        assert updated_user.hashed_password != "newpassword123"  # Должен быть захеширован
    
    def test_update_user_not_found(self, user_service):
        """Тест обновления несуществующего пользователя"""
        update_data = UserUpdate(username="new_username")
        updated_user = user_service.update_user(999, update_data)
        
        assert updated_user is None
    
    def test_delete_user_success(self, user_service, test_user_data):
        """Тест успешного удаления пользователя"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        
        success = user_service.delete_user(created_user.id)
        
        assert success is True
        
        # Проверяем, что пользователь действительно удален
        deleted_user = user_service.get_user_by_id(created_user.id)
        assert deleted_user is None
    
    def test_delete_user_not_found(self, user_service):
        """Тест удаления несуществующего пользователя"""
        success = user_service.delete_user(999)
        assert success is False
    
    def test_authenticate_user_success(self, user_service, test_user_data):
        """Тест успешной аутентификации пользователя"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        
        authenticated_user = user_service.authenticate_user(
            test_user_data["email"], 
            test_user_data["password"]
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == created_user.email
    
    def test_authenticate_user_invalid_email(self, user_service, test_user_data):
        """Тест аутентификации с неверным email"""
        user_data = UserCreate(**test_user_data)
        user_service.create_user(user_data)
        
        authenticated_user = user_service.authenticate_user(
            "wrong@example.com", 
            test_user_data["password"]
        )
        
        assert authenticated_user is None
    
    def test_authenticate_user_invalid_password(self, user_service, test_user_data):
        """Тест аутентификации с неверным паролем"""
        user_data = UserCreate(**test_user_data)
        user_service.create_user(user_data)
        
        authenticated_user = user_service.authenticate_user(
            test_user_data["email"], 
            "wrongpassword"
        )
        
        assert authenticated_user is None
    
    def test_password_hashing(self, user_service, test_user_data):
        """Тест хеширования паролей"""
        user_data = UserCreate(**test_user_data)
        user = user_service.create_user(user_data)
        
        # Проверяем, что пароль захеширован
        assert user.hashed_password != test_user_data["password"]
        assert user.hashed_password.startswith("$2b$")
        
        # Проверяем, что хеш можно верифицировать
        assert user_service._verify_password(test_user_data["password"], user.hashed_password)
        assert not user_service._verify_password("wrongpassword", user.hashed_password)
    
    def test_user_creation_timestamps(self, user_service, test_user_data):
        """Тест создания временных меток"""
        user_data = UserCreate(**test_user_data)
        user = user_service.create_user(user_data)
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at == user.updated_at  # При создании они должны быть равны
    
    def test_user_update_timestamp(self, user_service, test_user_data):
        """Тест обновления временной метки"""
        user_data = UserCreate(**test_user_data)
        created_user = user_service.create_user(user_data)
        original_updated_at = created_user.updated_at
        
        # Обновляем пользователя
        update_data = UserUpdate(username="updated_username")
        updated_user = user_service.update_user(created_user.id, update_data)
        
        assert updated_user.updated_at > original_updated_at
