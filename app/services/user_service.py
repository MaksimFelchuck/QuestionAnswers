from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import UserCreate, UserUpdate
from app.alembic.models.user import User
from fastapi import HTTPException, status
from app.core.logging import user_logger

# Настройка для хеширования паролей
from passlib.context import CryptContext

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
        user_logger.info(f"Creating user with email: {user_data.email}")
        
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
            user_logger.info(f"User created successfully with ID: {db_user.id}")
            return db_user
        except IntegrityError:
            self.db.rollback()
            user_logger.warning(f"Failed to create user with email {user_data.email}: duplicate email or username")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists"
            )

    def get_user_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        user_logger.debug(f"Getting user by ID: {user_id}")
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            user_logger.warning(f"User with ID {user_id} not found")
        return user

    def get_user_by_email(self, email: str) -> User | None:
        """Получить пользователя по email"""
        user_logger.debug(f"Getting user by email: {email}")
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            user_logger.warning(f"User with email {email} not found")
        return user

    def get_all_users(self) -> list[User]:
        """Получить всех пользователей"""
        user_logger.debug("Getting all users")
        return self.db.query(User).all()

    def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Обновить пользователя"""
        user_logger.info(f"Updating user with ID: {user_id}")
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            user_logger.warning(f"User with ID {user_id} not found for update")
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
            user_logger.info(f"User {user_id} updated successfully")
            return db_user
        except IntegrityError:
            self.db.rollback()
            user_logger.error(f"Failed to update user {user_id} due to integrity error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not update user, possibly duplicate email or username"
            )

    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        user_logger.info(f"Deleting user with ID: {user_id}")
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            user_logger.warning(f"User with ID {user_id} not found for deletion")
            return False

        self.db.delete(db_user)
        self.db.commit()
        user_logger.info(f"User {user_id} deleted successfully")
        return True

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Аутентификация пользователя"""
        user_logger.debug(f"Authenticating user with email: {email}")
        user = self.get_user_by_email(email)
        if not user:
            user_logger.warning(f"Authentication failed: user with email {email} not found")
            return None
        if not self._verify_password(password, user.hashed_password):
            user_logger.warning(f"Authentication failed: invalid password for user {email}")
            return None
        user_logger.info(f"User {email} authenticated successfully")
        return user
