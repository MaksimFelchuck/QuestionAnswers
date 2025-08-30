from abc import ABC, abstractmethod
from app.alembic.models.user import User
from app.models.user import UserCreate, UserUpdate

class UserRepository(ABC):
    """Абстрактный репозиторий для работы с пользователями"""
    
    @abstractmethod
    async def create(self, user: UserCreate) -> User:
        """Создать пользователя"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Получить пользователя по username"""
        pass
    
    @abstractmethod
    async def get_all(self) -> list[User]:
        """Получить всех пользователей"""
        pass
    
    @abstractmethod
    async def update(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Обновить пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        pass
    

