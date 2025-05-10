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
