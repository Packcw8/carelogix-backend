from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    agency_id: str  # Chosen from predefined list

class UserRead(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    agency_id: str
    is_admin: bool

from datetime import date, datetime
from typing import List, Any

class InvoiceRead(BaseModel):
    invoice_id: str
    user_id: str
    provider_name: str
    start_date: date
    end_date: date
    total: float
    created_at: datetime
    data: List[Any]  # Optional: you could define a detailed row structure later
