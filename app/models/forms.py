from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    form_type = Column(String)
    file_path = Column(String)
    case_name = Column(String, index=True)       # ✅ new
    case_number = Column(String, index=True)     # ✅ new
    context = Column(JSON)                       # ✅ new
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

