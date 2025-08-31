from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.question import QuestionCreate, QuestionUpdate
from app.alembic.models.question import Question
from app.alembic.models.answer import Answer
from fastapi import HTTPException, status
from app.core.logging import question_logger


class QuestionService:
    def __init__(self, db: Session):
        self.db = db

    def create_question(self, question_data: QuestionCreate) -> Question:
        """Создать новый вопрос"""
        question_logger.info(f"Creating question: {question_data.text[:50]}...")
        
        question = Question(text=question_data.text)
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        question_logger.info(f"Question created successfully with ID: {question.id}")
        return question

    def get_question_by_id(self, question_id: int) -> Question | None:
        """Получить вопрос по ID"""
        question_logger.debug(f"Getting question by ID: {question_id}")
        
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            question_logger.warning(f"Question with ID {question_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        return question

    def get_all_questions(self) -> list[Question]:
        """Получить все вопросы с количеством ответов"""
        question_logger.debug("Getting all questions with answer counts")
        
        questions = self.db.query(
            Question,
            func.count(Answer.id).label('answers_count')
        ).outerjoin(Answer).group_by(Question.id).all()
        
        # Преобразуем результат в список вопросов с добавлением количества ответов
        result = []
        for question, answers_count in questions:
            question.answers_count = answers_count
            result.append(question)
        
        question_logger.info(f"Retrieved {len(result)} questions")
        return result

    def update_question(self, question_id: int, question_data: QuestionUpdate) -> Question | None:
        """Обновить вопрос"""
        question_logger.info(f"Updating question with ID: {question_id}")
        
        question = self.get_question_by_id(question_id)
        
        update_data = question_data.model_dump(exclude_unset=True)
        # Исключаем None значения, чтобы не нарушить NOT NULL ограничения
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        for field, value in update_data.items():
            setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        
        question_logger.info(f"Question {question_id} updated successfully")
        return question

    def delete_question(self, question_id: int) -> bool:
        """Удалить вопрос (каскадно удалит все ответы)"""
        question_logger.info(f"Deleting question with ID: {question_id}")
        
        question = self.get_question_by_id(question_id)
        self.db.delete(question)
        self.db.commit()
        
        question_logger.info(f"Question {question_id} deleted successfully (with cascade)")
        return True

    def get_question_with_answers(self, question_id: int) -> Question | None:
        """Получить вопрос с ответами"""
        question_logger.debug(f"Getting question with answers by ID: {question_id}")
        
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            question_logger.warning(f"Question with ID {question_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Загружаем связанные ответы
        self.db.refresh(question)
        question_logger.info(f"Retrieved question {question_id} with {len(question.answers)} answers")
        return question
