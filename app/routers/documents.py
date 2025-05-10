from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from docxtpl import DocxTemplate
import uuid
import os

router = APIRouter()

class VisitForm(BaseModel):
    case_name: str
    case_number: str
    service_date: str
    start_time: str
    stop_time: str
    location: str
    service_provided: str
    code: str
    provider: str
    participants: str
    summary: str
    suplyneeds_checkbox: str
    rules_checkbox: str
    fosterspeak_checkbox: str
    foster_concerns: str
    safety_concerns: str
    additional_information: str
    miles: str
    tt_units: str
    itt_units: str
    signature: str
    travel_blocks: Optional[List[Dict[str, str]]] = []

@router.post("/generate-visit-doc")
def generate_doc(data: VisitForm):
    template_path = "app/Templates/supervised_visit.docx"
    doc = DocxTemplate(template_path)

    context = data.dict()
    output_dir = "generated_docs"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"visit_{uuid.uuid4()}.docx")
    doc.render(context)
    doc.save(output_path)

    return {"file_path": output_path}


