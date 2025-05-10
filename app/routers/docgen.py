from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.auth.auth_dependencies import get_current_user
from app.utils.doc_fill import fill_template
from pydantic import BaseModel
from app.models.forms import FormSubmission
from app.database import get_db
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import os
import re

router = APIRouter()

class TemplateData(BaseModel):
    template_name: str
    context: dict
    form_type: str  # required from frontend

def sanitize_filename(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '_', text.lower())

@router.post("/generate-doc")
def generate_doc(
    data: TemplateData,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # ✅ Generate a clean filename from context
        case_name = sanitize_filename(data.context.get("case_name", "case"))
        service_date = sanitize_filename(data.context.get("service_date", datetime.now().strftime("%B %d %Y")))
        filename = f"{case_name}_{service_date}.docx"

        # ✅ Generate the document using the clean filename
        path = fill_template(data.template_name, data.context, filename)

        # ✅ Store in database using clean name
        form_id = str(uuid4())
        db.add(FormSubmission(
            id=form_id,
            user_id=user.id,
            form_type=data.form_type,
            file_path=filename,  # Only the filename, not full path
            case_name=data.context.get("case_name"),
            case_number=data.context.get("case_number"),
            context=data.context,
        ))
        db.commit()

        return FileResponse(
            path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


