from fastapi import APIRouter, Depends, HTTPException
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
import boto3  # ✅ Boto3 for S3 integration

router = APIRouter()

class TemplateData(BaseModel):
    template_name: str
    context: dict
    form_type: str

def sanitize_filename(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '_', text.lower())

# ✅ S3 client using env variables
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
        # ✅ Clean filenames
        case_name = sanitize_filename(data.context.get("case_name", "case"))
        service_date = sanitize_filename(data.context.get("service_date", datetime.now().strftime("%B %d %Y")))
        filename_docx = f"{case_name}_{service_date}.docx"
        filename_pdf = filename_docx.replace(".docx", ".pdf")

        # ✅ Debug signature type
        sig_val = data.context.get("signature", "")
        print("🔍 Signature type:", "Image" if sig_val.startswith("data:image") else "Typed")

        # ✅ Generate both DOCX and PDF
        path_docx, path_pdf = fill_template(data.template_name, data.context, filename_docx)

        # ✅ Upload both to S3
        upload_to_s3(path_docx, filename_docx)
        upload_to_s3(path_pdf, filename_pdf)

        # ✅ Clean context for DB
        clean_context = dict(data.context)
        if isinstance(clean_context.get("signature"), (RichText, InlineImage)):
            clean_context["signature"] = "Signed"

        # ✅ Save to DB
        form_id = str(uuid4())
        db.add(FormSubmission(
            id=form_id,
            user_id=user.id,
            form_type=data.form_type,
            file_path=filename_docx,  # Store just the .docx path
            case_name=data.context.get("case_name"),
            case_number=data.context.get("case_number"),
            context=clean_context,
        ))
        db.commit()

        # ✅ Return S3 URLs
        bucket = os.getenv('S3_BUCKET_NAME')
        region = os.getenv('AWS_REGION')
        base_url = f"https://{bucket}.s3.{region}.amazonaws.com"

        return {
            "download_url_docx": f"{base_url}/{filename_docx}",
            "download_url_pdf": f"{base_url}/{filename_pdf}"
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))









