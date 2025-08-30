
from app.repositories.user.abstract import UserRepository
from app.alembic.models.user import User
from app.models.user import UserCreate, UserUpdate
from app.services.auth import get_password_hash

class InMemUserRepository(UserRepository):
    """InMemory репозиторий для тестов"""
    
    def __init__(self):
        self.users: list[User] = []
        self._counter = 1
    
    def _create_user_from_create(self, user_create: UserCreate) -> User:
        """Создание объекта User из UserCreate"""
        user = User(
            id=self._counter,
            username=user_create.username,
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
            is_active=True
        )
        self._counter += 1
        return user
    
    async def create(self, user: UserCreate) -> User:
        """Создать пользователя"""
        new_user = self._create_user_from_create(user)
        self.users.append(new_user)
        return new_user
    
    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email"""
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    async def get_by_username(self, username: str) -> User | None:
        """Получить пользователя по username"""
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    async def get_all(self) -> list[User]:
        """Получить всех пользователей"""
        return self.users.copy()
    
    async def update(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Обновить пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Просто обновляем поля - для InMem проверка уникальности не критична
        if user_update.username is not None:
            user.username = user_update.username
        
        if user_update.email is not None:
            user.email = user_update.email
        
        return user
    
    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        user = await self.get_by_id(user_id)
        if user:
            self.users.remove(user)
            return True
        return False
    

