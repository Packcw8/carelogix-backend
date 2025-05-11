from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.forms import FormSubmission
from app.auth.auth_dependencies import get_current_user

router = APIRouter()

@router.get("/generate-invoice")
def generate_invoice(
    week_start: str = Query(..., description="Start date of the week (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    start_date = datetime.strptime(week_start, "%Y-%m-%d")
    end_date = start_date + timedelta(days=6)

    submissions = db.query(FormSubmission).filter(
        FormSubmission.user_id == current_user.id,
        FormSubmission.created_at >= start_date,
        FormSubmission.created_at <= end_date,
    ).all()

    invoice_rows = []
    service_tracker = {}

    # Pull user tier and tier-based pay rates
    tier = getattr(current_user, "pay_tier", "Tier 1")
    TIER_PAY_RATES = {
        "Tier 1": {
            "Supervised Visit": 20,
            "ITT": 20,
            "MDT": 20,
            "Mileage": 0.66,
        },
        "Tier 2": {
            "Supervised Visit": 24,
            "ITT": 24,
            "MDT": 24,
            "Mileage": 0.66,
        },
        "Tier 3": {
            "Supervised Visit": 28,
            "ITT": 28,
            "MDT": 28,
            "Mileage": 0.66,
        },
    }

    for sub in submissions:
        ctx = sub.context
        client = ctx.get("case_name", "Unknown")
        case_number = ctx.get("case_number", "Unknown")
        service = ctx.get("service_provided", "Unknown")
        code = ctx.get("code", "Unknown")

        # Grouping key for merging same services
        key = (client, case_number, service, code)
        units = calculate_units(ctx.get("start_time"), ctx.get("stop_time"))
        rate = TIER_PAY_RATES.get(tier, {}).get(service, 25)

        if key not in service_tracker:
            service_tracker[key] = {
                "client_name": client,
                "case_number": case_number,
                "service": service,
                "service_code": code,
                "units": 0,
                "rate": rate,
            }

        service_tracker[key]["units"] += units

        # Separate rows for mileage, ITT, MDT using tiered rates
        if "miles" in ctx and ctx["miles"]:
            invoice_rows.append({
                "client_name": client,
                "case_number": case_number,
                "service": "Mileage",
                "service_code": "",
                "units": float(ctx["miles"]),
                "rate": TIER_PAY_RATES[tier]["Mileage"],
            })
        if "itt_units" in ctx:
            invoice_rows.append({
                "client_name": client,
                "case_number": case_number,
                "service": "ITT",
                "service_code": "",
                "units": int(ctx["itt_units"]),
                "rate": TIER_PAY_RATES[tier]["ITT"],
            })
        if "tt_units" in ctx:
            invoice_rows.append({
                "client_name": client,
                "case_number": case_number,
                "service": "MDT",
                "service_code": "",
                "units": int(ctx["tt_units"]),
                "rate": TIER_PAY_RATES[tier]["MDT"],
            })

    # Add merged service rows
    for row in service_tracker.values():
        invoice_rows.append(row)

    # Finalize total for each row
    for row in invoice_rows:
        row["total"] = round(row["units"] * row["rate"], 2)

    return invoice_rows


def calculate_units(start, stop):
    if not start or not stop:
        return 0
    try:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(stop, "%H:%M")
        minutes = max(0, int((e - s).total_seconds() / 60))
        return round(minutes / 15)
    except:
        return 0
