from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.answer_service import AnswerService
from app.models.answer import AnswerCreate, AnswerResponse
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()


@router.get("/", response_model=list[AnswerResponse], status_code=200)
async def get_answers(db: Session = Depends(get_db)):
    """Получить все ответы"""
    answer_service = AnswerService(db)
    answers = answer_service.get_all_answers()
    return answers


@router.post("/", response_model=AnswerResponse, status_code=201)
async def create_answer(
    answer_data: AnswerCreate, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новый ответ"""
    answer_service = AnswerService(db)
    answer = answer_service.create_answer(answer_data, current_user["email"])
    return answer


@router.get("/{answer_id}", response_model=AnswerResponse, status_code=200)
async def get_answer(answer_id: int, db: Session = Depends(get_db)):
    """Получить ответ по ID"""
    answer_service = AnswerService(db)
    answer = answer_service.get_answer_by_id(answer_id)
    return answer


@router.get("/question/{question_id}", response_model=list[AnswerResponse], status_code=200)
async def get_answers_by_question(question_id: int, db: Session = Depends(get_db)):
    """Получить все ответы на конкретный вопрос"""
    answer_service = AnswerService(db)
    answers = answer_service.get_answers_by_question_id(question_id)
    return answers


@router.get("/user/{user_id}", response_model=list[AnswerResponse], status_code=200)
async def get_answers_by_user(user_id: str, db: Session = Depends(get_db)):
    """Получить все ответы конкретного пользователя"""
    answer_service = AnswerService(db)
    answers = answer_service.get_answers_by_user_id(user_id)
    return answers


@router.delete("/{answer_id}", status_code=204)
async def delete_answer(
    answer_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить ответ (только автор может удалять)"""
    answer_service = AnswerService(db)
    answer_service.delete_answer(answer_id, current_user["email"])
    return None
