from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.database import get_db
from app.models import Client
from app.auth.auth_dependencies import get_current_user

router = APIRouter()

@router.post("/clients")
def add_client(
    case_name: str,
    case_number: str,
    client_number: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_client = Client(
        id=str(uuid4()),
        user_id=current_user.id,
        case_name=case_name,
        case_number=case_number,
        client_number=client_number,
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

@router.get("/clients")
def get_clients(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Client).filter(Client.user_id == current_user.id).all()

@router.delete("/clients/{client_id}")
def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id, Client.user_id == current_user.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"detail": "Client deleted"}
