from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
import os

from app.models.models import Referral

from app.database import get_db
from app.auth.auth_dependencies import get_current_user
from app.utils.s3 import s3, generate_presigned_url  # ✅ both S3 client & URL generator

router = APIRouter()

@router.post("/referrals/upload")
async def upload_referral(
    file: UploadFile = File(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Generate unique S3 key
    s3_key = f"referrals/{uuid4()}_{file.filename}"

    # Upload to S3
    bucket = os.getenv("S3_BUCKET_NAME")
    s3.upload_fileobj(file.file, bucket, s3_key)

    # Save referral in database
    referral = Referral(
        user_id=user.id,
        filename=file.filename,
        s3_key=s3_key,
        note=note,
    )
    db.add(referral)
    db.commit()

    return {"message": "Referral uploaded", "filename": file.filename}


@router.get("/referrals/mine")
def get_my_referrals(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    referrals = db.query(Referral).filter(Referral.user_id == user.id).all()
    result = []
    for ref in referrals:
        url = generate_presigned_url(ref.s3_key)
        result.append({
            "id": ref.id,
            "filename": ref.filename,
            "note": ref.note,
            "download_url": url
        })
    return result
