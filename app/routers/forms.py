import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.auth_dependencies import get_current_user
from app.auth.role_dependencies import require_admin
from app.models.forms import FormSubmission

router = APIRouter()

# Base S3 URL (update if needed)
S3_BASE_URL = "https://carelogix-docs.s3.us-east-2.amazonaws.com"

def build_form_response(f: FormSubmission):
    service_date = (
        f.context.get("service_date")
        if isinstance(f.context, dict)
        else json.loads(f.context).get("service_date")
    )

    filename = f.file_path.split("/")[-1]  # just the filename
    base_name = filename.replace(".docx", "")

    return {
        "id": f.id,
        "form_type": f.form_type,
        "file_path": f.file_path,
        "created_at": f.created_at,
        "case_name": f.case_name,
        "case_number": f.case_number,
        "service_date": service_date,
        "download_url_docx": f"{S3_BASE_URL}/{base_name}.docx",
        "download_url_pdf": f"{S3_BASE_URL}/{base_name}.pdf",
    }

@router.get("/forms/mine")
def get_user_forms(user=Depends(get_current_user), db: Session = Depends(get_db)):
    forms = db.query(FormSubmission).filter(FormSubmission.user_id == user.id).all()
    return [build_form_response(f) for f in forms]

@router.get("/forms/all")
def get_all_forms(admin=Depends(require_admin), db: Session = Depends(get_db)):
    forms = db.query(FormSubmission).all()
    return [build_form_response(f) for f in forms]

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
