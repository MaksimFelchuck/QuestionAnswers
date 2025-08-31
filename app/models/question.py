from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class QuestionBase(BaseModel):
    text: str


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: Optional[str] = None


class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    answers_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class QuestionWithAnswersResponse(QuestionBase):
    id: int
    created_at: datetime
    answers: List["AnswerResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# Обновляем модель для разрешения циклических ссылок
from app.models.answer import AnswerResponse
QuestionWithAnswersResponse.model_rebuild()
