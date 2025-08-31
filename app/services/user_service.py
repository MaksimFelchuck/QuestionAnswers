from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.alembic.models.user import User
from app.models.user import UserCreate, UserUpdate
from passlib.context import CryptContext
from fastapi import HTTPException, status
from typing import List, Optional

# Настройка для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        try:
            hashed_password = self._hash_password(user_data.password)
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists"
            )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_all_users(self) -> List[User]:
        """Получить всех пользователей"""
        return self.db.query(User).all()

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        
        # Если обновляется пароль, хешируем его
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists"
            )

    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.hashed_password):
            return None
        return user
