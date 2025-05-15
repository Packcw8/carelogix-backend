from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models import User, Agency
from app.database import get_db
from app.auth.auth_utils import hash_password
import uuid

router = APIRouter()

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    agency = db.query(Agency).filter(Agency.id == user.agency_id).first()
    if not agency:
        raise HTTPException(status_code=400, detail="Invalid agency ID")

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        agency_id=user.agency_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.get("/agencies")
def list_agencies(db: Session = Depends(get_db)):
    return [{"id": agency.id, "name": agency.name} for agency in db.query(Agency).all()]

@router.get("/debug/user/{email}")
def debug_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=email).first()
    if not user:
        return {"error": "User not found"}
    return {
        "email": user.email,
        "password_hash": user.password_hash
    }
@router.get("/debug/users-all")
def debug_users_all(db: Session = Depends(get_db)):
    return [user.email for user in db.query(User).all()]

