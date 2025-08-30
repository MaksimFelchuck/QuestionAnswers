from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.exceptions import UserNotFoundError, AuthenticationError, InvalidTokenError, UserAlreadyExistsError
from app.api.v1.api import api_router
from app.containers import Container

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors(), "status_code": 422}
    )

from sqlalchemy.exc import IntegrityError

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Обработка ошибок целостности базы данных"""
    return JSONResponse(
        status_code=409,
        content={"detail": "Data integrity violation", "status_code": 409}
    )

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "User not found", "status_code": 404}
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Authentication failed", "status_code": 401}
    )


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(request: Request, exc: InvalidTokenError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid token", "status_code": 401}
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": "User already exists", "status_code": 409}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

# Инициализация контейнера
container = Container()
container.config.from_dict({
    "database": {
        "url": settings.DATABASE_URL
    },
    "test_mode": False  # False для production
})

# Подключение контейнера к приложению через state
app.state.container = container

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to QuestionAnswers API"}
