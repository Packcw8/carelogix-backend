from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.models.forms import FormSubmission
from app.auth.auth_dependencies import get_current_user
from app.utils.s3 import generate_presigned_url  # ✅ adjust if needed

router = APIRouter()

# ✅ List all users in the same agency
@router.get("/admin/users")
def get_agency_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

# ✅ Get a user's forms (admin view) with download links
@router.get("/admin/users/{user_id}/forms")
def get_user_forms_by_admin(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    target_user = db.query(User).filter(
        User.id == user_id,
        User.agency_id == current_user.agency_id
    ).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found or not in your agency")

    forms = db.query(FormSubmission).filter(FormSubmission.user_id == user_id).order_by(FormSubmission.created_at.desc()).all()

    return [
        {
            "id": form.id,
            "form_type": form.form_type,
            "created_at": form.created_at,
            "case_name": form.case_name,
            "case_number": form.case_number,
            "service_date": form.context.get("service_date") if isinstance(form.context, dict) else None,
            "download_url_docx": generate_presigned_url(form.file_path),
            "download_url_pdf": generate_presigned_url(form.file_path.replace(".docx", ".pdf")),
        }
        for form in forms
    ]
