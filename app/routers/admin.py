from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db
from app.auth.auth_dependencies import get_current_user  # <- Adjust to match where your function is

router = APIRouter()

@router.get("/admin/users")
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "is_admin": user.is_admin,
            "agency_name": user.agency.name if user.agency else None,
        }
        for user in users
    ]
