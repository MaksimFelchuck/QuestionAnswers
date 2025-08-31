from sqlalchemy.orm import Session
from app.models.answer import AnswerCreate, AnswerUpdate
from app.alembic.models.answer import Answer
from app.alembic.models.question import Question
from fastapi import HTTPException, status
from app.core.logging import answer_logger


class AnswerService:
    def __init__(self, db: Session):
        self.db = db

    def create_answer(self, answer_data: AnswerCreate, user_id: str) -> Answer:
        """Создать новый ответ"""
        answer_logger.info(f"Creating answer for question {answer_data.question_id} by user {user_id}")
        
        # Проверяем, что вопрос существует
        question = self.db.query(Question).filter(Question.id == answer_data.question_id).first()
        if not question:
            answer_logger.warning(f"Question with ID {answer_data.question_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        answer = Answer(
            text=answer_data.text,
            question_id=answer_data.question_id,
            user_id=user_id
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        
        answer_logger.info(f"Answer created successfully with ID: {answer.id}")
        return answer

    def get_answer_by_id(self, answer_id: int) -> Answer | None:
        """Получить ответ по ID"""
        answer_logger.debug(f"Getting answer by ID: {answer_id}")
        
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            answer_logger.warning(f"Answer with ID {answer_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        return answer

    def get_answers_by_question_id(self, question_id: int) -> list[Answer]:
        """Получить все ответы на конкретный вопрос"""
        answer_logger.debug(f"Getting answers for question ID: {question_id}")
        
        # Проверяем, что вопрос существует
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            answer_logger.warning(f"Question with ID {question_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        answers = self.db.query(Answer).filter(Answer.question_id == question_id).all()
        answer_logger.info(f"Retrieved {len(answers)} answers for question {question_id}")
        return answers

    def get_answers_by_user_id(self, user_id: str) -> list[Answer]:
        """Получить все ответы конкретного пользователя"""
        answer_logger.debug(f"Getting answers for user ID: {user_id}")
        
        answers = self.db.query(Answer).filter(Answer.user_id == user_id).all()
        answer_logger.info(f"Retrieved {len(answers)} answers for user {user_id}")
        return answers

    def update_answer(self, answer_id: int, answer_data: AnswerUpdate, user_id: str) -> Answer | None:
        """Обновить ответ (только автор может обновлять)"""
        answer_logger.info(f"Updating answer {answer_id} by user {user_id}")
        
        answer = self.get_answer_by_id(answer_id)
        
        # Проверяем, что пользователь является автором ответа
        if answer.user_id != user_id:
            answer_logger.warning(f"User {user_id} attempted to update answer {answer_id} owned by {answer.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own answers"
            )
        
        update_data = answer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(answer, field, value)
        
        self.db.commit()
        self.db.refresh(answer)
        
        answer_logger.info(f"Answer {answer_id} updated successfully")
        return answer

    def delete_answer(self, answer_id: int, user_id: str) -> bool:
        """Удалить ответ (только автор может удалять)"""
        answer_logger.info(f"Deleting answer {answer_id} by user {user_id}")
        
        answer = self.get_answer_by_id(answer_id)
        
        # Проверяем, что пользователь является автором ответа
        if answer.user_id != user_id:
            answer_logger.warning(f"User {user_id} attempted to delete answer {answer_id} owned by {answer.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own answers"
            )
        
        self.db.delete(answer)
        self.db.commit()
        
        answer_logger.info(f"Answer {answer_id} deleted successfully")
        return True

    def get_all_answers(self) -> list[Answer]:
        """Получить все ответы"""
        answer_logger.debug("Getting all answers")
        
        answers = self.db.query(Answer).all()
        answer_logger.info(f"Retrieved {len(answers)} answers")
        return answers
