import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.services.user_service import UserService


# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределяем зависимость для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Подменяем зависимость
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Тестовый клиент"""
    # Создаем таблицы для тестов
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Очищаем после тестов
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Автоматически очищает базу данных перед каждым тестом"""
    yield
    # Очищаем все данные после каждого теста
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM users"))
            conn.commit()
    except Exception:
        # Игнорируем ошибки, если таблица не существует
        pass


@pytest.fixture
def db_session():
    """Сессия базы данных для тестов"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_service(db_session):
    """Сервис пользователей для тестов"""
    return UserService(db_session)


@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def test_user_data2():
    """Вторые тестовые данные пользователя"""
    return {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpassword456"
    }
