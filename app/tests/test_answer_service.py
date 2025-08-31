import pytest
from fastapi import HTTPException
from app.services.answer_service import AnswerService
from app.services.question_service import QuestionService
from app.models.answer import AnswerCreate
from app.models.question import QuestionCreate


class TestAnswerService:
    def test_create_answer_success(self, db_session):
        """Тест успешного создания ответа"""
        # Создаем вопрос
        question_service = QuestionService(db_session)
        question = question_service.create_question(QuestionCreate(text="What is FastAPI?"))
        
        answer_service = AnswerService(db_session)
        answer_data = AnswerCreate(question_id=question.id, text="FastAPI is a modern web framework")
        answer = answer_service.create_answer(answer_data, "user123")
        
        assert answer.text == "FastAPI is a modern web framework"
        assert answer.question_id == question.id
        assert answer.user_id == "user123"
        assert answer.id is not None
        assert answer.created_at is not None

    def test_create_answer_question_not_found(self, db_session):
        """Тест создания ответа к несуществующему вопросу"""
        answer_service = AnswerService(db_session)
        answer_data = AnswerCreate(question_id=999, text="This should fail")
        
        with pytest.raises(HTTPException) as exc_info:
            answer_service.create_answer(answer_data, "user123")
        
        assert exc_info.value.status_code == 404
        assert "Question not found" in str(exc_info.value.detail)

    def test_get_answer_by_id_success(self, db_session):
        """Тест успешного получения ответа по ID"""
        # Создаем вопрос и ответ
        question_service = QuestionService(db_session)
        question = question_service.create_question(QuestionCreate(text="What is FastAPI?"))
        
        answer_service = AnswerService(db_session)
        answer_data = AnswerCreate(question_id=question.id, text="FastAPI is a modern web framework")
        created_answer = answer_service.create_answer(answer_data, "user123")
        
        retrieved_answer = answer_service.get_answer_by_id(created_answer.id)
        
        assert retrieved_answer.id == created_answer.id
        assert retrieved_answer.text == created_answer.text
        assert retrieved_answer.question_id == created_answer.question_id

    def test_get_answer_by_id_not_found(self, db_session):
        """Тест получения несуществующего ответа по ID"""
        answer_service = AnswerService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            answer_service.get_answer_by_id(999)
        
        assert exc_info.value.status_code == 404
        assert "Answer not found" in str(exc_info.value.detail)

    def test_get_answers_by_question_id_success(self, db_session):
        """Тест получения всех ответов на конкретный вопрос"""
        # Создаем вопрос
        question_service = QuestionService(db_session)
        question = question_service.create_question(QuestionCreate(text="What is FastAPI?"))
        
        answer_service = AnswerService(db_session)
        
        # Создаем несколько ответов на один вопрос
        answer1 = answer_service.create_answer(
            AnswerCreate(question_id=question.id, text="Answer 1"), "user1"
        )
        answer2 = answer_service.create_answer(
            AnswerCreate(question_id=question.id, text="Answer 2"), "user2"
        )
        
        answers = answer_service.get_answers_by_question_id(question.id)
        
        assert len(answers) == 2
        assert answers[0].text == "Answer 1"
        assert answers[1].text == "Answer 2"

    def test_get_answers_by_question_id_not_found(self, db_session):
        """Тест получения ответов несуществующего вопроса"""
        answer_service = AnswerService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            answer_service.get_answers_by_question_id(999)
        
        assert exc_info.value.status_code == 404
        assert "Question not found" in str(exc_info.value.detail)

    def test_get_answers_by_user_id_success(self, db_session):
        """Тест получения всех ответов конкретного пользователя"""
        # Создаем вопрос
        question_service = QuestionService(db_session)
        question = question_service.create_question(QuestionCreate(text="What is FastAPI?"))
        
        answer_service = AnswerService(db_session)
        
        # Создаем несколько ответов от одного пользователя
        answer1 = answer_service.create_answer(
            AnswerCreate(question_id=question.id, text="Answer 1"), "user1"
        )
        answer2 = answer_service.create_answer(
            AnswerCreate(question_id=question.id, text="Answer 2"), "user1"
        )
        
        user1_answers = answer_service.get_answers_by_user_id("user1")
        
        assert len(user1_answers) == 2
        assert all(answer.user_id == "user1" for answer in user1_answers)

    def test_delete_answer_success(self, db_session):
        """Тест успешного удаления ответа"""
        # Создаем вопрос и ответ
        question_service = QuestionService(db_session)
        question = question_service.create_question(QuestionCreate(text="What is FastAPI?"))
        
        answer_service = AnswerService(db_session)
        answer_data = AnswerCreate(question_id=question.id, text="Answer to delete")
        answer = answer_service.create_answer(answer_data, "user123")
        
        result = answer_service.delete_answer(answer.id, "user123")
        
        assert result is True
        
        # Проверяем, что ответ действительно удален
        with pytest.raises(HTTPException) as exc_info:
            answer_service.get_answer_by_id(answer.id)
        
        assert exc_info.value.status_code == 404

    def test_delete_answer_unauthorized(self, db_session):
        """Тест удаления ответа неавторизованным пользователем"""
        # Создаем вопрос и ответ
        question_service = QuestionService(db_session)
        question = question_service.create_question(QuestionCreate(text="What is FastAPI?"))
        
        answer_service = AnswerService(db_session)
        answer_data = AnswerCreate(question_id=question.id, text="Answer to delete")
        answer = answer_service.create_answer(answer_data, "user123")
        
        with pytest.raises(HTTPException) as exc_info:
            answer_service.delete_answer(answer.id, "different_user")
        
        assert exc_info.value.status_code == 403
        assert "You can only delete your own answers" in str(exc_info.value.detail)

    def test_get_all_answers_empty(self, db_session):
        """Тест получения всех ответов (пустой список)"""
        answer_service = AnswerService(db_session)
        answers = answer_service.get_all_answers()
        
        assert answers == []

    def test_get_all_answers_with_data(self, db_session):
        """Тест получения всех ответов с данными"""
        # Создаем вопрос
        question_service = QuestionService(db_session)
        question = question_service.create_question(QuestionCreate(text="What is FastAPI?"))
        
        answer_service = AnswerService(db_session)
        
        # Создаем несколько ответов
        answer1 = answer_service.create_answer(
            AnswerCreate(question_id=question.id, text="Answer 1"), "user1"
        )
        answer2 = answer_service.create_answer(
            AnswerCreate(question_id=question.id, text="Answer 2"), "user2"
        )
        
        all_answers = answer_service.get_all_answers()
        
        assert len(all_answers) == 2
        assert all_answers[0].text == "Answer 1"
        assert all_answers[1].text == "Answer 2"
