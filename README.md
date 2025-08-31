# QuestionAnswers API

Современное REST API для системы вопросов и ответов, построенное на FastAPI с использованием PostgreSQL и JWT аутентификации.

## 🏗️ Архитектура

### Технологический стек:
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **Alembic** - система миграций
- **JWT** - аутентификация и авторизация
- **Pydantic** - валидация данных
- **Docker** - контейнеризация

### Структура проекта:
```
QuestionAnswers/
├── app/
│   ├── alembic/           # Миграции базы данных
│   │   ├── models/        # SQLAlchemy модели
│   │   └── versions/      # Файлы миграций
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/ # API эндпоинты
│   │       └── api.py     # Роутер API
│   ├── core/              # Конфигурация и база данных
│   ├── models/            # Pydantic модели
│   ├── services/          # Бизнес-логика
│   └── main.py           # Точка входа приложения
├── app/tests/             # Тесты
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Docker Compose конфигурация
└── requirements.txt      # Python зависимости
```

## 📊 Модели данных

### User (Пользователь)
- `id` - уникальный идентификатор
- `username` - имя пользователя (уникальное)
- `email` - email (уникальный)
- `hashed_password` - хешированный пароль
- `is_active` - статус активности
- `created_at` - время создания
- `updated_at` - время обновления

### Question (Вопрос)
- `id` - уникальный идентификатор
- `text` - текст вопроса
- `created_at` - время создания
- `answers` - связь с ответами (каскадное удаление)

### Answer (Ответ)
- `id` - уникальный идентификатор
- `question_id` - ссылка на вопрос
- `user_id` - идентификатор пользователя (email)
- `text` - текст ответа
- `created_at` - время создания

## 🔒 Логика безопасности

### Аутентификация:
- JWT токены (access + refresh)
- Хеширование паролей с bcrypt
- Автоматическое обновление токенов

### Авторизация:
- **Вопросы**: публичный доступ на чтение и создание без авторизации
- **Ответы**: создание и удаление только авторизованными пользователями
- **Пользователи**: полный CRUD доступ без авторизации

### Валидация:
- ✅ Нельзя создать ответ к несуществующему вопросу
- ✅ Один пользователь может оставлять несколько ответов на один вопрос
- ✅ При удалении вопроса каскадно удаляются все его ответы
- ✅ Только автор может удалять свои ответы
- ✅ **Вопросы и ответы нельзя редактировать** (только создавать и удалять)

## 🚀 Запуск через Docker

### Предварительные требования:
- Docker
- Docker Compose

### Быстрый запуск:

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd QuestionAnswers
```

2. **Запустите приложение:**
```bash
docker-compose up --build
```

3. **Откройте браузер:**
- API документация: http://localhost:8000/docs
- Альтернативная документация: http://localhost:8000/redoc

### Остановка:
```bash
docker-compose down
```

### Остановка с удалением данных:
```bash
docker-compose down -v
```

## 🔧 Конфигурация

### Переменные окружения:
```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/questionanswers
SECRET_KEY=your-secret-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Изменение конфигурации:
1. Отредактируйте `docker-compose.yml`
2. Перезапустите контейнеры:
```bash
docker-compose down
docker-compose up --build
```

## 📚 API Endpoints

### Пользователи (`/api/v1/users/`)
| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| POST | `/register` | Регистрация | ❌ |
| POST | `/login` | Вход | ❌ |
| POST | `/refresh` | Обновление токена | ❌ |
| GET | `/me` | Информация о текущем пользователе | ✅ |
| GET | `/` | Список всех пользователей | ❌ |
| GET | `/{user_id}` | Получить пользователя по ID | ❌ |
| PUT | `/{user_id}` | Обновить пользователя | ❌ |
| DELETE | `/{user_id}` | Удалить пользователя | ❌ |

### Вопросы (`/api/v1/questions/`)
| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/` | Список всех вопросов | ❌ |
| POST | `/` | Создать вопрос | ❌ |
| GET | `/{question_id}` | Получить вопрос по ID | ❌ |
| GET | `/{question_id}/with-answers` | Вопрос со всеми ответами | ❌ |
| DELETE | `/{question_id}` | Удалить вопрос (каскадно) | ❌ |

### Ответы (`/api/v1/answers/`)
| Метод | Endpoint | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/` | Список всех ответов | ❌ |
| POST | `/` | Создать ответ | ✅ |
| GET | `/{answer_id}` | Получить ответ по ID | ❌ |
| GET | `/question/{question_id}` | Ответы на конкретный вопрос | ❌ |
| GET | `/user/{user_id}` | Ответы конкретного пользователя | ❌ |
| DELETE | `/{answer_id}` | Удалить ответ (только автор) | ✅ |

## 🧪 Тестирование

### Запуск тестов:
```bash
# Все тесты
docker-compose exec app python -m pytest app/tests/ -v

# Конкретные тесты
docker-compose exec app python -m pytest app/tests/test_users_api.py -v
docker-compose exec app python -m pytest app/tests/test_questions_api.py -v
docker-compose exec app python -m pytest app/tests/test_answers_api.py -v
```

### Покрытие тестами:
- **103 теста** покрывают все основные функции
- **Unit тесты** для сервисов
- **Integration тесты** для API эндпоинтов
- **Валидация** бизнес-логики и безопасности

### Тестовые сценарии:
- ✅ Создание, чтение, удаление пользователей
- ✅ Аутентификация и авторизация
- ✅ Создание, чтение, удаление вопросов
- ✅ Создание, чтение, удаление ответов
- ✅ Каскадное удаление ответов при удалении вопроса
- ✅ Проверка на создание ответа к несуществующему вопросу
- ✅ Проверка на множественные ответы одного пользователя
- ✅ Проверка прав доступа (только автор может удалять ответы)

## 🔄 Миграции базы данных

### Создание новой миграции:
```bash
docker-compose exec app alembic revision --autogenerate -m "Description"
```

### Применение миграций:
```bash
docker-compose exec app alembic upgrade head
```

### Откат миграции:
```bash
docker-compose exec app alembic downgrade -1
```

## 📝 Примеры использования

### 1. Регистрация и вход пользователя:
```bash
# Регистрация
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "secret123"}'

# Вход
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secret123"}'
```

### 2. Создание вопроса:
```bash
curl -X POST "http://localhost:8000/api/v1/questions/" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is FastAPI?"}'
```

### 3. Создание ответа (требует аутентификации):
```bash
curl -X POST "http://localhost:8000/api/v1/answers/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"question_id": 1, "text": "FastAPI is a modern web framework for Python"}'
```

### 4. Получение вопроса со всеми ответами:
```bash
curl -X GET "http://localhost:8000/api/v1/questions/1/with-answers"
```

### 5. Удаление ответа (только автор):
```bash
curl -X DELETE "http://localhost:8000/api/v1/answers/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛠️ Разработка

### Локальная разработка:
1. Установите Python 3.12+
2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте базу данных:
```bash
# Создайте .env файл с переменными окружения
# Запустите миграции
alembic upgrade head
```

5. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

### Структура кода:
- **Сервисы** содержат бизнес-логику
- **Эндпоинты** обрабатывают HTTP запросы
- **Модели** определяют структуру данных
- **Тесты** обеспечивают качество кода

## 📈 Мониторинг и логирование

### Логирование:
- Настроено стандартное Python логирование
- Логи выводятся в консоль и файлы
- Различные уровни логирования (DEBUG, INFO, WARNING, ERROR)

### Health Check:
```bash
curl http://localhost:8000/health
```

### Логи:
```bash
# Просмотр логов приложения
docker-compose logs app

# Просмотр логов базы данных
docker-compose logs db

# Следить за логами в реальном времени
docker-compose logs -f app
```

## 🔐 Безопасность

### Рекомендации для продакшена:
1. Измените `SECRET_KEY` на уникальный
2. Настройте HTTPS
3. Ограничьте доступ к базе данных
4. Настройте rate limiting
5. Добавьте CORS настройки
6. Используйте переменные окружения для секретов

### Пример .env файла:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/questionanswers
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚨 Важные особенности

### Иммутабельность контента:
- **Вопросы и ответы нельзя редактировать** после создания
- Это обеспечивает целостность данных и предотвращает случайные изменения
- Для изменения контента нужно удалить и создать заново

### Каскадное удаление:
- При удалении вопроса автоматически удаляются все связанные ответы
- Это предотвращает появление "сиротских" ответов

### Множественные ответы:
- Один пользователь может оставлять несколько ответов на один вопрос
- Это позволяет пользователям дополнять свои ответы

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs app`
2. Убедитесь, что база данных запущена
3. Проверьте переменные окружения
4. Создайте Issue в репозитории

---

**Версия**: 2.0.0  
**Автор**: QuestionAnswers Team  
**Последнее обновление**: 2024  
**Статус**: Все тесты проходят (103/103) ✅
