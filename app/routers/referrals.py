@router.post("/referrals/upload")
async def upload_referral(
    file: UploadFile = File(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.utils.s3 import s3  # Optional: if not already imported

    # Generate unique S3 key
    s3_key = f"referrals/{uuid4()}_{file.filename}"
    bucket = os.getenv("S3_BUCKET_NAME")

    # ✅ Upload to S3 with inline Content-Disposition
    s3.upload_fileobj(
        Fileobj=file.file,
        Bucket=bucket,
        Key=s3_key,
        ExtraArgs={
            "ContentDisposition": "inline",  # ✅ allows browser preview
            "ContentType": file.content_type  # optional but helpful
        }
    )

    # Save referral in DB
    referral = Referral(
        user_id=user.id,
        filename=file.filename,
        s3_key=s3_key,
        note=note,
    )
    db.add(referral)
    db.commit()

    return {"message": "Referral uploaded", "filename": file.filename}
