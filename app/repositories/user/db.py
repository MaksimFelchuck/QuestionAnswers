
from sqlalchemy.orm import Session

from app.repositories.user.abstract import UserRepository
from app.alembic.models.user import User
from app.models.user import UserCreate, UserUpdate
from app.services.auth import get_password_hash

class DBUserRepository(UserRepository):
    """Репозиторий для работы с пользователями в базе данных"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, user: UserCreate) -> User:
        """Создать пользователя"""
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password),
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_by_username(self, username: str) -> User | None:
        """Получить пользователя по username"""
        return self.db.query(User).filter(User.username == username).first()
    
    async def get_all(self) -> list[User]:
        """Получить всех пользователей"""
        return self.db.query(User).all()
    
    async def update(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Обновить пользователя"""
        update_data = user_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return await self.get_by_id(user_id)
        
        # Просто обновляем - база данных сама проверит уникальность
        result = self.db.query(User).filter(User.id == user_id).update(update_data)
        
        if result == 0:
            return None
        
        self.db.commit()
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        db_user = await self.get_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    

