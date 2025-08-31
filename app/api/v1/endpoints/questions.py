from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.question_service import QuestionService
from app.models.question import QuestionCreate, QuestionResponse, QuestionWithAnswersResponse

router = APIRouter()


@router.get("/", response_model=list[QuestionResponse], status_code=200)
async def get_questions(db: Session = Depends(get_db)):
    """Получить все вопросы с количеством ответов"""
    question_service = QuestionService(db)
    questions = question_service.get_all_questions()
    return questions


@router.post("/", response_model=QuestionResponse, status_code=201)
async def create_question(question_data: QuestionCreate, db: Session = Depends(get_db)):
    """Создать новый вопрос"""
    question_service = QuestionService(db)
    question = question_service.create_question(question_data)
    return question


@router.get("/{question_id}", response_model=QuestionResponse, status_code=200)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    """Получить вопрос по ID"""
    question_service = QuestionService(db)
    question = question_service.get_question_by_id(question_id)
    return question


@router.get("/{question_id}/with-answers", response_model=QuestionWithAnswersResponse, status_code=200)
async def get_question_with_answers(question_id: int, db: Session = Depends(get_db)):
    """Получить вопрос со всеми ответами"""
    question_service = QuestionService(db)
    question = question_service.get_question_with_answers(question_id)
    return question


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Удалить вопрос (каскадно удалятся все ответы)"""
    question_service = QuestionService(db)
    question_service.delete_question(question_id)
    return None
