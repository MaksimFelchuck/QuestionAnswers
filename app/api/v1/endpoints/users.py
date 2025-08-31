from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.services.auth_service import create_access_token, create_refresh_token, verify_token
from app.models.user import (
    UserCreate, UserResponse, UserUpdate, UserLogin, 
    Token, RefreshToken
)
from datetime import timedelta
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Получить текущего пользователя из токена"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {"email": email, "user_id": user_id}


@router.get("/", response_model=list[UserResponse], status_code=200)
async def get_users(db: Session = Depends(get_db)):
    """Получить список всех пользователей"""
    user_service = UserService(db)
    users = user_service.get_all_users()
    return users


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token, status_code=200)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Авторизация пользователя"""
    user_service = UserService(db)
    
    # Аутентифицируем пользователя
    user = user_service.authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
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


@router.post("/refresh", response_model=Token, status_code=200)
async def refresh_token(refresh_data: RefreshToken, db: Session = Depends(get_db)):
    """Обновление access токена через refresh токен"""
    user_service = UserService(db)
    
    # Проверяем refresh токен
    payload = verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Получаем пользователя
    user = user_service.get_user_by_email(email)
    if not user or user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
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


@router.get("/me", response_model=UserResponse, status_code=200)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Получить информацию о текущем пользователе"""
    user_service = UserService(db)
    email = current_user["email"]
    user = user_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/{user_id}", response_model=UserResponse, status_code=200)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse, status_code=200)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Обновить пользователя"""
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя"""
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None
