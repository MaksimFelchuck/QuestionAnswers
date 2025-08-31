from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, UTC


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relationship with answers
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
