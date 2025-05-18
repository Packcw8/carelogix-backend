from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List
from pydantic import BaseModel

from ..database import get_db
from ..models import Client, User
from .auth import get_current_user

router = APIRouter()

class ClientCreate(BaseModel):
    case_name: str
    case_number: str
    client_number: str
    case_worker: str = ""
    worker_email: str = ""
    address: str = ""
    phone_number: str = ""
    participants: str = ""

class ClientRead(ClientCreate):
    id: str

@router.post("/clients", response_model=ClientRead)
def add_client(client_data: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_client = Client(
        id=str(uuid4()),
        user_id=current_user.id,
        case_name=client_data.case_name,
        case_number=client_data.case_number,
        client_number=client_data.client_number,
        case_worker=client_data.case_worker,
        worker_email=client_data.worker_email,
        address=client_data.address,
        phone_number=client_data.phone_number,
        participants=client_data.participants,
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

@router.get("/clients", response_model=List[ClientRead])
def get_clients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Client).filter(Client.user_id == current_user.id).all()

@router.delete("/clients/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    client = db.query(Client).filter(Client.id == client_id, Client.user_id == current_user.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "Client deleted"}
