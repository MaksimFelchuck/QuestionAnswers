from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class AnswerBase(BaseModel):
    text: str


class AnswerCreate(AnswerBase):
    question_id: int


class AnswerUpdate(BaseModel):
    text: Optional[str] = None


class AnswerResponse(AnswerBase):
    id: int
    question_id: int
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
