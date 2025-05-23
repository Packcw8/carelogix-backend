from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models import Client, User
from app.auth.auth_dependencies import get_current_user

router = APIRouter()

# ---------------------
# Pydantic Schemas
# ---------------------

class ClientCreate(BaseModel):
    case_name: str
    case_number: str
    client_number: str
    case_worker: Optional[str] = None
    worker_email: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    participants: Optional[str] = None


class ClientResponse(BaseModel):
    id: str  # UUID string
    case_name: str
    case_number: str
    client_number: str
    case_worker: Optional[str] = None
    worker_email: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    participants: Optional[str] = None

    class Config:
        orm_mode = True

# ---------------------
# Routes
# ---------------------

@router.post("/clients", response_model=ClientResponse)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_client = Client(
        case_name=client.case_name,
        case_number=client.case_number,
        client_number=client.client_number,
        case_worker=client.case_worker,
        worker_email=client.worker_email,
        address=client.address,
        phone_number=client.phone_number,
        participants=client.participants,
        user_id=current_user.id,
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/clients", response_model=List[ClientResponse])
def get_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Client).filter(Client.user_id == current_user.id).all()


@router.delete("/clients/{client_id}")
def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.user_id == current_user.id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(client)
    db.commit()
    return {"detail": "Client deleted"}
