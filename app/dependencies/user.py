from fastapi import Depends
from app.dependencies.dependencies import get_user_repository
from app.repositories.user.abstract import UserRepository
from app.models.user import UserCreate, UserResponse, UserUpdate, UserLogin, Token
from app.alembic.models.user import User
from app.services.auth import create_access_token, create_refresh_token, verify_token
from app.dependencies.auth import authenticate_user
from app.models.user import RefreshToken
from app.core.exceptions import UserNotFoundError, AuthenticationError, InvalidTokenError
from datetime import timedelta
from app.core.config import settings


async def create_user(user_data: UserCreate, user_repo: UserRepository = Depends(get_user_repository)) -> UserResponse:
    """Создать нового пользователя"""
    user = await user_repo.create(user_data)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )





async def get_user_by_id(user_id: int, user_repo: UserRepository = Depends(get_user_repository)) -> UserResponse:
    """Получить пользователя по ID"""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


async def get_user_by_email(email: str, user_repo: UserRepository = Depends(get_user_repository)) -> UserResponse:
    """Получить пользователя по email"""
    user = await user_repo.get_by_email(email)
    if not user:
        raise UserNotFoundError(f"User with email {email} not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


async def get_all_users(user_repo: UserRepository = Depends(get_user_repository)) -> list[UserResponse]:
    """Получить всех пользователей"""
    users = await user_repo.get_all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]





async def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """Обновить пользователя"""
    user = await user_repo.update(user_id, user_data)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


async def delete_user(user_id: int, user_repo: UserRepository = Depends(get_user_repository)) -> dict:
    """Удалить пользователя"""
    success = await user_repo.delete(user_id)
    if not success:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    return {"message": "User successfully deleted"}


async def login_user(user_credentials: UserLogin, user_repo: UserRepository = Depends(get_user_repository)) -> Token:
    """Авторизация пользователя"""
    # Аутентифицируем пользователя
    user = await authenticate_user(user_credentials.email, user_credentials.password, user_repo)
    if not user:
        raise AuthenticationError("Invalid email or password")
    
    # Создаем токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )





async def refresh_user_token(refresh_data: RefreshToken, user_repo: UserRepository = Depends(get_user_repository)) -> Token:
    """Обновление access токена через refresh токен"""
    # Проверяем refresh токен
    payload = verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid refresh token")
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not user_id:
        raise InvalidTokenError("Invalid refresh token")
    
    # Получаем пользователя
    user = await user_repo.get_by_email(email)
    
    if not user or user.id != user_id:
        raise UserNotFoundError("User not found")
    
    # Создаем новые токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )





async def get_current_user_info(current_user: dict, user_repo: UserRepository = Depends(get_user_repository)) -> UserResponse:
    """Получить информацию о текущем пользователе"""
    email = current_user["sub"]
    user_id = current_user["user_id"]
    
    user = await user_repo.get_by_email(email)
    if not user or user.id != user_id:
        raise UserNotFoundError("User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )












