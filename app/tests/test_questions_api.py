import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestQuestionAPI:
    def test_get_questions_empty(self, client: TestClient):
        """Тест получения всех вопросов (пустой список)"""
        response = client.get("/api/v1/questions/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_question_success(self, client: TestClient):
        """Тест успешного создания вопроса"""
        question_data = {"text": "What is FastAPI?"}
        response = client.post("/api/v1/questions/", json=question_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["text"] == "What is FastAPI?"
        assert data["id"] is not None
        assert data["created_at"] is not None

    def test_create_question_missing_text(self, client: TestClient):
        """Тест создания вопроса без текста"""
        question_data = {}
        response = client.post("/api/v1/questions/", json=question_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_question_by_id_success(self, client: TestClient):
        """Тест получения вопроса по ID"""
        # Создаем вопрос
        question_data = {"text": "What is FastAPI?"}
        create_response = client.post("/api/v1/questions/", json=question_data)
        question_id = create_response.json()["id"]
        
        # Получаем вопрос по ID
        response = client.get(f"/api/v1/questions/{question_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == question_id
        assert data["text"] == "What is FastAPI?"

    def test_get_question_by_id_not_found(self, client: TestClient):
        """Тест получения несуществующего вопроса"""
        response = client.get("/api/v1/questions/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Question not found" in response.json()["detail"]

    def test_get_questions_with_data(self, client: TestClient):
        """Тест получения всех вопросов с данными"""
        # Создаем несколько вопросов
        question1_data = {"text": "Question 1"}
        question2_data = {"text": "Question 2"}
        
        client.post("/api/v1/questions/", json=question1_data)
        client.post("/api/v1/questions/", json=question2_data)
        
        # Получаем все вопросы
        response = client.get("/api/v1/questions/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["text"] == "Question 1"
        assert data[1]["text"] == "Question 2"

    def test_delete_question_success(self, client: TestClient):
        """Тест успешного удаления вопроса"""
        # Создаем вопрос
        question_data = {"text": "Question to delete"}
        create_response = client.post("/api/v1/questions/", json=question_data)
        question_id = create_response.json()["id"]
        
        # Удаляем вопрос
        response = client.delete(f"/api/v1/questions/{question_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что вопрос действительно удален
        get_response = client.get(f"/api/v1/questions/{question_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_question_with_answers_cascade(self, client: TestClient, test_user_data: dict):
        """Тест каскадного удаления ответов при удалении вопроса"""
        # Регистрируем и авторизуем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Создаем вопрос
        question_data = {"text": "Question with answers"}
        question_response = client.post("/api/v1/questions/", json=question_data)
        question_id = question_response.json()["id"]
        
        # Создаем несколько ответов на этот вопрос
        answer1_data = {"question_id": question_id, "text": "Answer 1"}
        answer2_data = {"question_id": question_id, "text": "Answer 2"}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        answer1_response = client.post("/api/v1/answers/", json=answer1_data, headers=headers)
        answer2_response = client.post("/api/v1/answers/", json=answer2_data, headers=headers)
        
        answer1_id = answer1_response.json()["id"]
        answer2_id = answer2_response.json()["id"]
        
        # Проверяем, что ответы созданы
        answers_response = client.get(f"/api/v1/answers/question/{question_id}")
        assert len(answers_response.json()) == 2
        
        # Удаляем вопрос
        delete_response = client.delete(f"/api/v1/questions/{question_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что вопрос удален
        question_get_response = client.get(f"/api/v1/questions/{question_id}")
        assert question_get_response.status_code == status.HTTP_404_NOT_FOUND
        
        # Проверяем, что все ответы каскадно удалены
        answer1_get_response = client.get(f"/api/v1/answers/{answer1_id}")
        answer2_get_response = client.get(f"/api/v1/answers/{answer2_id}")
        assert answer1_get_response.status_code == status.HTTP_404_NOT_FOUND
        assert answer2_get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_question_not_found(self, client: TestClient):
        """Тест удаления несуществующего вопроса"""
        response = client.delete("/api/v1/questions/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Question not found" in response.json()["detail"]

    def test_get_question_with_answers_success(self, client: TestClient, test_user_data: dict):
        """Тест получения вопроса со всеми ответами"""
        # Регистрируем и авторизуем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Создаем вопрос
        question_data = {"text": "What is FastAPI?"}
        question_response = client.post("/api/v1/questions/", json=question_data)
        question_id = question_response.json()["id"]
        
        # Создаем несколько ответов
        answer1_data = {"question_id": question_id, "text": "FastAPI is a modern web framework"}
        answer2_data = {"question_id": question_id, "text": "It's built on top of Starlette"}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        client.post("/api/v1/answers/", json=answer1_data, headers=headers)
        client.post("/api/v1/answers/", json=answer2_data, headers=headers)
        
        # Получаем вопрос со всеми ответами
        response = client.get(f"/api/v1/questions/{question_id}/with-answers")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == question_id
        assert data["text"] == "What is FastAPI?"
        assert len(data["answers"]) == 2
        assert data["answers"][0]["text"] == "FastAPI is a modern web framework"
        assert data["answers"][1]["text"] == "It's built on top of Starlette"

    def test_get_question_with_answers_not_found(self, client: TestClient):
        """Тест получения несуществующего вопроса со ответами"""
        response = client.get("/api/v1/questions/999/with-answers")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Question not found" in response.json()["detail"]
