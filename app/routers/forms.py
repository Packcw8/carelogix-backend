import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.auth_dependencies import get_current_user
from app.auth.role_dependencies import require_admin
from app.models.forms import FormSubmission

router = APIRouter()

@router.get("/forms/mine")
def get_user_forms(user=Depends(get_current_user), db: Session = Depends(get_db)):
    forms = db.query(FormSubmission).filter(FormSubmission.user_id == user.id).all()
    return [
        {
            "id": f.id,
            "form_type": f.form_type,
            "file_path": f.file_path,
            "created_at": f.created_at,
            "case_name": f.case_name,
            "case_number": f.case_number,
            "service_date": (
                f.context.get("service_date")
                if isinstance(f.context, dict)
                else json.loads(f.context).get("service_date")
            ),
        }
        for f in forms
    ]

@router.get("/forms/all")
def get_all_forms(admin=Depends(require_admin), db: Session = Depends(get_db)):
    forms = db.query(FormSubmission).all()
    return [
        {
            "id": f.id,
            "form_type": f.form_type,
            "file_path": f.file_path,
            "created_at": f.created_at,
            "case_name": f.case_name,
            "case_number": f.case_number,
            "service_date": (
                f.context.get("service_date")
                if isinstance(f.context, dict)
                else json.loads(f.context).get("service_date")
            ),
        }
        for f in forms
    ]

from fastapi import HTTPException

@router.delete("/forms/{form_id}")
def delete_form(form_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    form = db.query(FormSubmission).filter(
        FormSubmission.id == form_id,
        FormSubmission.user_id == user.id  # Prevent deleting others' forms
    ).first()

    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    db.delete(form)
    db.commit()
    return {"message": "Form deleted"}


