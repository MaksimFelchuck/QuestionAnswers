from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseResponse, BaseCreate, BaseUpdate

class AnswerCreate(BaseCreate):
    content: str = Field(..., min_length=1, max_length=5000, description="Содержание ответа")
    question_id: int = Field(..., description="ID вопроса")

class AnswerUpdate(BaseUpdate):
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="Содержание ответа")

class AnswerResponse(BaseResponse):
    content: str
    question_id: int
    author_id: int
    is_accepted: bool = False
    votes_count: int = 0
