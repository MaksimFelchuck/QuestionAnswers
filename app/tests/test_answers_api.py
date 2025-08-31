import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestAnswerAPI:
    def test_get_answers_empty(self, client: TestClient):
        """Тест получения всех ответов (пустой список)"""
        response = client.get("/api/v1/answers/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_answer_success(self, client: TestClient, test_user_data: dict):
        """Тест успешного создания ответа"""
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
        
        # Создаем ответ
        answer_data = {
            "question_id": question_id,
            "text": "FastAPI is a modern web framework"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/answers/", json=answer_data, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["text"] == "FastAPI is a modern web framework"
        assert data["question_id"] == question_id
        assert data["id"] is not None
        assert data["created_at"] is not None

    def test_create_answer_without_auth(self, client: TestClient):
        """Тест создания ответа без авторизации"""
        answer_data = {
            "question_id": 1,
            "text": "This should fail"
        }
        response = client.post("/api/v1/answers/", json=answer_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_answer_question_not_found(self, client: TestClient, test_user_data: dict):
        """Тест создания ответа к несуществующему вопросу"""
        # Регистрируем и авторизуем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Пытаемся создать ответ к несуществующему вопросу
        answer_data = {
            "question_id": 999,
            "text": "This should fail"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/answers/", json=answer_data, headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Question not found" in response.json()["detail"]

    def test_get_answer_by_id_success(self, client: TestClient, test_user_data: dict):
        """Тест получения ответа по ID"""
        # Создаем вопрос и ответ
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        question_data = {"text": "What is FastAPI?"}
        question_response = client.post("/api/v1/questions/", json=question_data)
        question_id = question_response.json()["id"]
        
        answer_data = {
            "question_id": question_id,
            "text": "FastAPI is a modern web framework"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        create_response = client.post("/api/v1/answers/", json=answer_data, headers=headers)
        answer_id = create_response.json()["id"]
        
        # Получаем ответ по ID
        response = client.get(f"/api/v1/answers/{answer_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == answer_id
        assert data["text"] == "FastAPI is a modern web framework"

    def test_get_answer_by_id_not_found(self, client: TestClient):
        """Тест получения несуществующего ответа"""
        response = client.get("/api/v1/answers/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Answer not found" in response.json()["detail"]

    def test_get_answers_by_question_success(self, client: TestClient, test_user_data: dict):
        """Тест получения всех ответов на конкретный вопрос"""
        # Создаем вопрос и несколько ответов
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        question_data = {"text": "What is FastAPI?"}
        question_response = client.post("/api/v1/questions/", json=question_data)
        question_id = question_response.json()["id"]
        
        # Создаем несколько ответов
        answer1_data = {"question_id": question_id, "text": "Answer 1"}
        answer2_data = {"question_id": question_id, "text": "Answer 2"}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        client.post("/api/v1/answers/", json=answer1_data, headers=headers)
        client.post("/api/v1/answers/", json=answer2_data, headers=headers)
        
        # Получаем все ответы на вопрос
        response = client.get(f"/api/v1/answers/question/{question_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["text"] == "Answer 1"
        assert data[1]["text"] == "Answer 2"

    def test_get_answers_by_question_not_found(self, client: TestClient):
        """Тест получения ответов несуществующего вопроса"""
        response = client.get("/api/v1/answers/question/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Question not found" in response.json()["detail"]

    def test_get_answers_by_user_success(self, client: TestClient, test_user_data: dict):
        """Тест получения всех ответов конкретного пользователя"""
        # Создаем пользователя и его ответы
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        question_data = {"text": "What is FastAPI?"}
        question_response = client.post("/api/v1/questions/", json=question_data)
        question_id = question_response.json()["id"]
        
        # Создаем несколько ответов от одного пользователя
        answer1_data = {"question_id": question_id, "text": "Answer 1"}
        answer2_data = {"question_id": question_id, "text": "Answer 2"}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        client.post("/api/v1/answers/", json=answer1_data, headers=headers)
        client.post("/api/v1/answers/", json=answer2_data, headers=headers)
        
        # Получаем все ответы пользователя
        user_id = test_user_data["email"]  # Используем email как user_id
        response = client.get(f"/api/v1/answers/user/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(answer["user_id"] == user_id for answer in data)

    def test_delete_answer_success(self, client: TestClient, test_user_data: dict):
        """Тест успешного удаления ответа"""
        # Создаем вопрос и ответ
        client.post("/api/v1/users/register", json=test_user_data)
        login_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token = login_response.json()["access_token"]
        
        question_data = {"text": "What is FastAPI?"}
        question_response = client.post("/api/v1/questions/", json=question_data)
        question_id = question_response.json()["id"]
        
        answer_data = {"question_id": question_id, "text": "Answer to delete"}
        headers = {"Authorization": f"Bearer {access_token}"}
        create_response = client.post("/api/v1/answers/", json=answer_data, headers=headers)
        answer_id = create_response.json()["id"]
        
        # Удаляем ответ
        response = client.delete(f"/api/v1/answers/{answer_id}", headers=headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что ответ действительно удален
        get_response = client.get(f"/api/v1/answers/{answer_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_answer_unauthorized(self, client: TestClient, test_user_data: dict, test_user_data2: dict):
        """Тест удаления ответа неавторизованным пользователем"""
        # Создаем двух пользователей
        client.post("/api/v1/users/register", json=test_user_data)
        client.post("/api/v1/users/register", json=test_user_data2)
        
        # Первый пользователь создает ответ
        login1_response = client.post("/api/v1/users/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        access_token1 = login1_response.json()["access_token"]
        
        question_data = {"text": "What is FastAPI?"}
        question_response = client.post("/api/v1/questions/", json=question_data)
        question_id = question_response.json()["id"]
        
        answer_data = {"question_id": question_id, "text": "Answer to delete"}
        headers1 = {"Authorization": f"Bearer {access_token1}"}
        create_response = client.post("/api/v1/answers/", json=answer_data, headers=headers1)
        answer_id = create_response.json()["id"]
        
        # Второй пользователь пытается удалить ответ
        login2_response = client.post("/api/v1/users/login", json={
            "email": test_user_data2["email"],
            "password": test_user_data2["password"]
        })
        access_token2 = login2_response.json()["access_token"]
        
        headers2 = {"Authorization": f"Bearer {access_token2}"}
        response = client.delete(f"/api/v1/answers/{answer_id}", headers=headers2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "You can only delete your own answers" in response.json()["detail"]

    def test_multiple_answers_same_user_same_question(self, client: TestClient, test_user_data: dict):
        """Тест создания нескольких ответов одним пользователем на один вопрос"""
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
        
        # Создаем несколько ответов от одного пользователя на один вопрос
        answer1_data = {"question_id": question_id, "text": "First answer"}
        answer2_data = {"question_id": question_id, "text": "Second answer"}
        answer3_data = {"question_id": question_id, "text": "Third answer"}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response1 = client.post("/api/v1/answers/", json=answer1_data, headers=headers)
        response2 = client.post("/api/v1/answers/", json=answer2_data, headers=headers)
        response3 = client.post("/api/v1/answers/", json=answer3_data, headers=headers)
        
        # Все ответы должны быть созданы успешно
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert response3.status_code == status.HTTP_201_CREATED
        
        # Проверяем, что все ответы созданы
        answers_response = client.get(f"/api/v1/answers/question/{question_id}")
        assert len(answers_response.json()) == 3
