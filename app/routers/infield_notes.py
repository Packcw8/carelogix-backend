from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app.database import get_db
from app.auth.auth_dependencies import get_current_user
from app.models.infield_note import InfieldNote
from app.schemas.infield_note import NoteCreate, NoteOut
from typing import List
from datetime import datetime

router = APIRouter(prefix="/infield-notes", tags=["Infield Notes"])

@router.post("/", response_model=NoteOut)
def create_note(note: NoteCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    new_note = InfieldNote(
        user_id=user.id,
        case_name=note.case_name,
        case_number=note.case_number,
        content=note.content,
        cleaned_summary=note.cleaned_summary,
        participants=note.participants,
        visit_details=note.visit_details,
        visit_date=note.visit_date,
        created_at=datetime.utcnow(),
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.get("/mine", response_model=List[NoteOut])
def get_my_notes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(InfieldNote)
        .filter(InfieldNote.user_id == user.id)
        .order_by(InfieldNote.created_at.desc())
        .all()
    )

@router.delete("/{note_id}")
def delete_note(note_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    note = db.query(InfieldNote).filter(InfieldNote.id == note_id, InfieldNote.user_id == user.id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found or unauthorized.")

    db.delete(note)
    db.commit()
    return {"message": "Note deleted"}
