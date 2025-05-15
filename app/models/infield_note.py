from sqlalchemy import Column, String, Text, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from app.database import Base

class InfieldNote(Base):
    __tablename__ = "infield_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    case_name = Column(String, nullable=False)
    case_number = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    cleaned_summary = Column(Text, nullable=True)
    participants = Column(Text, nullable=True)
    visit_details = Column(Text, nullable=True)
    visit_date = Column(Date, nullable=True)  # ✅ New: AI-extracted date
    created_at = Column(DateTime, default=datetime.utcnow)
