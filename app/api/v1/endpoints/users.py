from fastapi import APIRouter, Depends
from app.dependencies.user import (
    create_user, get_all_users, login_user,
    refresh_user_token, get_current_user_info,
    get_user_by_id, update_user, delete_user
)
from app.models.user import (
    UserCreate, UserResponse, UserUpdate, UserLogin, 
    Token, RefreshToken
)
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def get_users():
    """Получить список всех пользователей"""
    return await get_all_users()


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Регистрация нового пользователя"""
    # Проверка email уже есть в Pydantic модели через EmailStr
    return await create_user(user_data)


@router.post("/login", response_model=Token)
async def login_user_endpoint(user_credentials: UserLogin):
    """Авторизация пользователя"""
    return await login_user(user_credentials)


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(refresh_data: RefreshToken):
    """Обновление access токена через refresh токен"""
    return await refresh_user_token(refresh_data)





@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: dict = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return await get_current_user_info(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Получить пользователя по ID"""
    return await get_user_by_id(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user_data: UserUpdate):
    """Обновить пользователя"""
    return await update_user(user_id, user_data)


@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int):
    """Удалить пользователя"""
    return await delete_user(user_id)
