from fastapi import APIRouter, Depends
from app.auth.auth_dependencies import get_current_user
from app.models import User

router = APIRouter()

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "agency_id": current_user.agency_id,
        "is_admin": current_user.is_admin,
    }
