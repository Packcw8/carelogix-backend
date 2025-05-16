from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.forms import FormSubmission

router = APIRouter()

@router.get("/summaries/{client_name}/{month}")
def get_summaries_by_client_and_month(client_name: str, month: str, db: Session = Depends(get_db)):
    """
    Get all summaries for a given client and month.
    month = '2025-05'
    """
    results = db.query(FormSubmission).filter(
        FormSubmission.case_name == client_name,
        FormSubmission.service_date.like(f"{month}%"),
        FormSubmission.summary.isnot(None)
    ).all()

    return {
        "client": client_name,
        "month": month,
        "summaries": [f.summary for f in results if f.summary]
    }
