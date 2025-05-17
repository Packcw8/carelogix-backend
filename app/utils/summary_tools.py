# app/utils/summary_tools.py

from sqlalchemy.orm import Session
from app.models.forms import FormSubmission
from typing import List, Dict

def fetch_summaries_and_services(case_name: str, case_number: str, db: Session) -> (str, List[Dict]):
    forms = db.query(FormSubmission).filter(
        (FormSubmission.case_name == case_name) |
        (FormSubmission.case_number == case_number)
    ).order_by(FormSubmission.service_date).all()

    summaries = []
    services = []

    for form in forms:
        ctx = form.context or {}

        # Extract summary
        if "summary" in ctx and ctx["summary"]:
            summaries.append(f"- {form.service_date}: {ctx['summary']}")

        # Extract service entry
        service_entry = {
            "service_date": form.service_date,
            "service": ctx.get("service_provided", form.form_type),
            "start_time": ctx.get("start_time", ""),
            "stop_time": ctx.get("stop_time", ""),
            "participants": ctx.get("participants", ""),
            "milage": ctx.get("miles", "")  # 'miles' in context, 'milage' in template
        }

        # Only include if we have at least a date and a service
        if service_entry["service_date"] and service_entry["service"]:
            services.append(service_entry)

    return ("\n".join(summaries), services)
