from fastapi import APIRouter
from app.api.v1.endpoints import users

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
# api_router.include_router(answers.router, prefix="/answers", tags=["answers"])
