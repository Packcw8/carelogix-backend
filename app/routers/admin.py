from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.auth_dependencies import get_current_user  # adjust path if needed

router = APIRouter()

@router.get("/admin/users")
def get_agency_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    users = db.query(User).filter(User.agency_id == current_user.agency_id).all()
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
