from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BaseResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class BaseCreate(BaseModel):
    pass

class BaseUpdate(BaseModel):
    pass
