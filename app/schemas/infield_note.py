from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class NoteCreate(BaseModel):
    case_name: str
    case_number: str
    content: str

class NoteOut(BaseModel):
    id: UUID
    case_name: str
    case_number: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True  # ✅ updated for Pydantic v2
