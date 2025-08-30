from fastapi import Depends
from app.containers import Container


def get_container() -> Container:
    """Получить контейнер из app state"""
    from app.main import app
    return app.state.container


def get_user_repository(container: Container = Depends(get_container)):
    """Получить репозиторий пользователей"""
    return container.user_repository()


def get_question_repository(container: Container = Depends(get_container)):
    """Получить репозиторий вопросов"""
    return container.question_repository()


def get_answer_repository(container: Container = Depends(get_container)):
    """Получить репозиторий ответов"""
    return container.answer_repository()
