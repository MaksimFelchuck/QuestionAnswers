import pytest
from fastapi import HTTPException
from app.services.question_service import QuestionService
from app.models.question import QuestionCreate


class TestQuestionService:
    def test_create_question_success(self, db_session):
        """Тест успешного создания вопроса"""
        question_service = QuestionService(db_session)
        question_data = QuestionCreate(text="What is FastAPI?")
        question = question_service.create_question(question_data)
        
        assert question.text == "What is FastAPI?"
        assert question.id is not None
        assert question.created_at is not None

    def test_get_question_by_id_success(self, db_session):
        """Тест успешного получения вопроса по ID"""
        question_service = QuestionService(db_session)
        question_data = QuestionCreate(text="What is FastAPI?")
        created_question = question_service.create_question(question_data)
        
        retrieved_question = question_service.get_question_by_id(created_question.id)
        
        assert retrieved_question.id == created_question.id
        assert retrieved_question.text == created_question.text

    def test_get_question_by_id_not_found(self, db_session):
        """Тест получения несуществующего вопроса по ID"""
        question_service = QuestionService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            question_service.get_question_by_id(999)
        
        assert exc_info.value.status_code == 404
        assert "Question not found" in str(exc_info.value.detail)

    def test_get_all_questions_empty(self, db_session):
        """Тест получения всех вопросов (пустой список)"""
        question_service = QuestionService(db_session)
        questions = question_service.get_all_questions()
        
        assert len(questions) == 0

    def test_get_all_questions_with_data(self, db_session):
        """Тест получения всех вопросов с данными"""
        question_service = QuestionService(db_session)
        
        # Создаем несколько вопросов
        question1 = question_service.create_question(QuestionCreate(text="Question 1"))
        question2 = question_service.create_question(QuestionCreate(text="Question 2"))
        
        questions = question_service.get_all_questions()
        
        assert len(questions) == 2
        assert questions[0].text == "Question 1"
        assert questions[1].text == "Question 2"
        assert questions[0].answers_count == 0
        assert questions[1].answers_count == 0

    def test_delete_question_success(self, db_session):
        """Тест успешного удаления вопроса"""
        question_service = QuestionService(db_session)
        question_data = QuestionCreate(text="Question to delete")
        question = question_service.create_question(question_data)
        
        result = question_service.delete_question(question.id)
        
        assert result is True
        
        # Проверяем, что вопрос действительно удален
        with pytest.raises(HTTPException) as exc_info:
            question_service.get_question_by_id(question.id)
        
        assert exc_info.value.status_code == 404

    def test_delete_question_not_found(self, db_session):
        """Тест удаления несуществующего вопроса"""
        question_service = QuestionService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            question_service.delete_question(999)
        
        assert exc_info.value.status_code == 404
        assert "Question not found" in str(exc_info.value.detail)

    def test_get_question_with_answers_success(self, db_session):
        """Тест получения вопроса со всеми ответами"""
        question_service = QuestionService(db_session)
        question_data = QuestionCreate(text="Question with answers")
        question = question_service.create_question(question_data)
        
        retrieved_question = question_service.get_question_with_answers(question.id)
        
        assert retrieved_question.id == question.id
        assert retrieved_question.text == question.text
        assert hasattr(retrieved_question, 'answers')

    def test_get_question_with_answers_not_found(self, db_session):
        """Тест получения несуществующего вопроса со всеми ответами"""
        question_service = QuestionService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            question_service.get_question_with_answers(999)
        
        assert exc_info.value.status_code == 404
        assert "Question not found" in str(exc_info.value.detail)
