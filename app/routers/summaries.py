from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.forms import FormSubmission

router = APIRouter()

@router.get("/summaries/{client_name}/{month}")
def get_monthly_summary_data(client_name: str, month: str, db: Session = Depends(get_db)):
    """
    Return all relevant data for the Monthly Summary Form for a given client and month.
    """
    results = db.query(FormSubmission).filter(
        FormSubmission.case_name == client_name,
        FormSubmission.service_date.like(f"{month}%")
    ).all()

    summaries = []
    service_dates = set()
    participants = set()
    total_mileage = 0

    for form in results:
        if form.summary:
            summaries.append(form.summary)
        if form.service_date:
            service_dates.add(str(form.service_date))
        if form.participants:
            participants.add(form.participants)
        if form.miles:
            try:
                total_mileage += float(form.miles)
            except ValueError:
                continue

    return {
        "client": client_name,
        "month": month,
        "summaries": summaries,
        "service_dates": sorted(service_dates),
        "participants": list(participants),
        "mileage": str(total_mileage)
    }
