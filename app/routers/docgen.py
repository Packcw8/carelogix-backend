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
import traceback
from docxtpl import RichText, InlineImage
import boto3  # ✅ Import Boto3 for S3 integration

router = APIRouter()

class TemplateData(BaseModel):
    template_name: str
    context: dict
    form_type: str

def sanitize_filename(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '_', text.lower())

# ✅ S3 client setup using environment variables
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

def upload_to_s3(file_path: str, filename: str):
    bucket = os.getenv('S3_BUCKET_NAME')
    s3.upload_file(file_path, bucket, filename)

@router.post("/generate-doc")
def generate_doc(
    data: TemplateData,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        case_name = sanitize_filename(data.context.get("case_name", "case"))
        service_date = sanitize_filename(data.context.get("service_date", datetime.now().strftime("%B %d %Y")))
        filename = f"{case_name}_{service_date}.docx"

        sig_val = data.context.get("signature", "")
        print("🔍 Signature type:", "Image" if sig_val.startswith("data:image") else "Typed")

        # ✅ Generate the Word document locally
        path = fill_template(data.template_name, data.context, filename)

        # ✅ Upload to S3
        upload_to_s3(path, filename)

        # ✅ Strip non-serializable values before saving to DB
        clean_context = dict(data.context)
        if isinstance(clean_context.get("signature"), (RichText, InlineImage)):
            clean_context["signature"] = "Signed"

        # ✅ Save form record to database
        form_id = str(uuid4())
        db.add(FormSubmission(
            id=form_id,
            user_id=user.id,
            form_type=data.form_type,
            file_path=filename,  # You could optionally save full S3 URL here
            case_name=data.context.get("case_name"),
            case_number=data.context.get("case_number"),
            context=clean_context,
        ))
        db.commit()

        return FileResponse(
            path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))






