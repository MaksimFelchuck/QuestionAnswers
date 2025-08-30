from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import verify_token
from app.dependencies.dependencies import get_user_repository
from app.repositories.user.abstract import UserRepository

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получить текущего пользователя из токена"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )
    
    return {"email": email, "user_id": user_id}


async def authenticate_user(email: str, password: str, user_repo: UserRepository = Depends(get_user_repository)):
    """Аутентификация пользователя по email и паролю"""
    from app.services.auth import verify_password
    
    # Получаем пользователя по email
    user = await user_repo.get_by_email(email)
    if not user:
        return None
    
    # Проверяем пароль
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
