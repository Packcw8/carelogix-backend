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
import boto3

# ✅ Add import
from app.utils.summary_tools import fetch_summaries_and_services

router = APIRouter()

class TemplateData(BaseModel):
    template_name: str
    context: dict
    form_type: str

def sanitize_filename(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '_', text.lower())

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

def upload_to_s3(file_path: str, filename: str):
    bucket = os.getenv('S3_BUCKET_NAME')
    extra_args = {}
    if filename.endswith(".pdf"):
        extra_args = {
            "ContentType": "application/pdf",
            "ContentDisposition": "inline"
        }
    s3.upload_file(file_path, bucket, filename, ExtraArgs=extra_args)

def generate_presigned_url(filename: str) -> str:
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': os.getenv('S3_BUCKET_NAME'), 'Key': filename},
        ExpiresIn=3600  # 1 hour
    )

@router.post("/generate-doc")
def generate_doc(
    data: TemplateData,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # ✅ Normalize service_date
        raw_date = data.context.get("service_date")
        if isinstance(raw_date, str) and "T" in raw_date:
            raw_date = raw_date.split("T")[0]
        elif not raw_date:
            raw_date = datetime.utcnow().strftime("%Y-%m-%d")

        # ✅ Clean fields for filenames
        case_name = sanitize_filename(data.context.get("case_name", "case"))
        service_date_clean = sanitize_filename(raw_date)
        form_type_clean = sanitize_filename(data.form_type or "form")

        filename_docx = f"{case_name}_{service_date_clean}_{form_type_clean}.docx"
        filename_pdf = f"{case_name}_{service_date_clean}_{form_type_clean}.pdf"

        # ✅ Inject summaries and services if generating a Monthly Summary
        if data.template_name == "monthlysummary.docx":
            client_name = data.context.get("case_name")
            client_number = data.context.get("case_number")
            if client_name or client_number:
                auto_summary, auto_services = fetch_summaries_and_services(client_name, client_number, db)
                data.context["summaries"] = auto_summary
                data.context["services"] = auto_services

        # ✅ Debug signature type
        sig_val = data.context.get("signature", "")
        print("🔍 Signature type:", "Image" if sig_val.startswith("data:image") else "Typed")

        # ✅ Generate DOCX + PDF
        path_docx, path_pdf = fill_template(data.template_name, data.context, filename_docx)

        # ✅ Upload to S3
        upload_to_s3(path_docx, filename_docx)
        upload_to_s3(path_pdf, filename_pdf)

        # ✅ Clean up context before saving
        clean_context = dict(data.context)
        if isinstance(clean_context.get("signature"), (RichText, InlineImage)):
            clean_context["signature"] = "Signed"

        # ✅ Extract summary and related data
        summary_text = data.context.get("summary", "")
        client_number = data.context.get("client_number", "")
        participants = data.context.get("participants", "")
        miles = data.context.get("miles", "0")

        # ✅ Save to FormSubmission
        form_id = str(uuid4())
        db.add(FormSubmission(
            id=form_id,
            user_id=user.id,
            form_type=data.form_type,
            file_path=filename_docx,
            case_name=data.context.get("case_name"),
            case_number=data.context.get("case_number"),
            client_number=client_number,
            service_date=raw_date,
            summary=summary_text,
            participants=participants,
            miles=miles,
            context=clean_context,
        ))
        db.commit()

        return {
            "download_url_docx": generate_presigned_url(filename_docx),
            "download_url_pdf": generate_presigned_url(filename_pdf)
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
