from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, date

class NoteCreate(BaseModel):
    case_name: str
    case_number: str
    content: str
    cleaned_summary: Optional[str] = None
    participants: Optional[str] = None
    visit_details: Optional[str] = None
    visit_date: Optional[date] = None

class NoteOut(NoteCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
