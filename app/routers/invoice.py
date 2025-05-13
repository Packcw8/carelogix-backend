from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from app.database import get_db
from app.models.forms import FormSubmission
from app.models.models import Invoice, User
from app.auth.auth_dependencies import get_current_user
from app.auth.role_dependencies import require_admin

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

    tier = getattr(current_user, "pay_tier", "Tier 1")
    TIER_PAY_RATES = {
        "Tier 1": {"Supervised Visit": 20, "ITT": 20, "MDT": 20, "Mileage": 0.66},
        "Tier 2": {"Supervised Visit": 24, "ITT": 24, "MDT": 24, "Mileage": 0.66},
        "Tier 3": {"Supervised Visit": 28, "ITT": 28, "MDT": 28, "Mileage": 0.66},
    }

    for sub in submissions:
        ctx = sub.context
        client = ctx.get("case_name", "Unknown")
        case_number = ctx.get("case_number", "Unknown")
        client_number = ctx.get("client_number", "N/A")
        service = ctx.get("service_provided", "Unknown")
        code = ctx.get("code", "Unknown")

        key = (client, case_number, client_number, service, code)
        units = calculate_units(ctx.get("start_time"), ctx.get("stop_time"))
        rate = TIER_PAY_RATES.get(tier, {}).get(service, 25)

        if key not in service_tracker:
            service_tracker[key] = {
                "client_name": client,
                "case_number": case_number,
                "client_number": client_number,
                "service": service,
                "service_code": code,
                "units": 0,
                "rate": rate,
            }

        service_tracker[key]["units"] += units

        if "miles" in ctx and ctx["miles"]:
            invoice_rows.append({
                "client_name": client,
                "case_number": case_number,
                "client_number": client_number,
                "service": "Mileage",
                "service_code": "",
                "units": float(ctx["miles"]),
                "rate": TIER_PAY_RATES[tier]["Mileage"],
            })
        if "itt_units" in ctx:
            invoice_rows.append({
                "client_name": client,
                "case_number": case_number,
                "client_number": client_number,
                "service": "ITT",
                "service_code": "",
                "units": int(ctx["itt_units"]),
                "rate": TIER_PAY_RATES[tier]["ITT"],
            })
        if "tt_units" in ctx:
            invoice_rows.append({
                "client_name": client,
                "case_number": case_number,
                "client_number": client_number,
                "service": "MDT",
                "service_code": "",
                "units": int(ctx["tt_units"]),
                "rate": TIER_PAY_RATES[tier]["MDT"],
            })

    for row in service_tracker.values():
        invoice_rows.append(row)

    for row in invoice_rows:
        row["total"] = round(row["units"] * row["rate"], 2)

    return invoice_rows


@router.post("/save-invoice")
def save_invoice(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    invoice_data: list[dict] = Body(...),
):
    try:
        total = round(sum(row.get("units", 0) * row.get("rate", 0) for row in invoice_data), 2)

        invoice = Invoice(
            user_id=current_user.id,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
            total=total,
            data=invoice_data,
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        return {"message": "Invoice saved", "invoice_id": invoice.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save invoice: {str(e)}")


@router.get("/invoices/all")
def get_all_agency_invoices(
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    try:
        invoices = (
            db.query(Invoice)
            .join(User, Invoice.user_id == User.id)
            .options(joinedload(Invoice.user))
            .filter(User.agency_id == current_admin.agency_id)
            .all()
        )

        return [
            {
                "invoice_id": inv.id,
                "user_id": inv.user_id,
                "provider_name": inv.user.full_name,
                "start_date": inv.start_date,
                "end_date": inv.end_date,
                "total": inv.total,
                "created_at": inv.created_at,
                "data": inv.data,
            }
            for inv in invoices
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load invoices: {str(e)}")

@router.get("/invoices/mine")
def get_my_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        invoices = (
            db.query(Invoice)
            .filter(Invoice.user_id == current_user.id)
            .order_by(Invoice.created_at.desc())
            .all()
        )

        return [
            {
                "invoice_id": inv.id,
                "start_date": inv.start_date,
                "end_date": inv.end_date,
                "total": inv.total,
                "created_at": inv.created_at,
                "data": inv.data,
            }
            for inv in invoices
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load your invoices: {str(e)}")

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
