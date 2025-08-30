from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseResponse, BaseCreate, BaseUpdate

class QuestionCreate(BaseCreate):
    title: str = Field(..., min_length=1, max_length=200, description="Заголовок вопроса")
    content: str = Field(..., min_length=1, max_length=5000, description="Содержание вопроса")
    tags: Optional[List[str]] = Field(default=[], description="Теги вопроса")

class QuestionUpdate(BaseUpdate):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Заголовок вопроса")
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="Содержание вопроса")
    tags: Optional[List[str]] = Field(None, description="Теги вопроса")

class QuestionResponse(BaseResponse):
    title: str
    content: str
    tags: List[str]
    author_id: int
    answers_count: int = 0
    votes_count: int = 0
