from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.auth_dependencies import get_current_user
import openai
import os
import traceback
import json

print("🔍 OpenAI SDK loaded from:", openai.__file__)
print("🔢 OpenAI SDK version:", openai.__version__)

router = APIRouter()

class NoteInput(BaseModel):
    content: str

@router.post("/ai/clean-note")
async def clean_note(input: NoteInput, user=Depends(get_current_user)):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        prompt = f"""
You are a documentation assistant helping a family services provider summarize supervised visits, transports, and skill-based classes (e.g., Adult Life Skills, Parenting Classes, etc.).

Your task is to take the raw infield notes below and extract:
1. A professional, fully detailed summary in the third person (refer to "the provider").
2. A list of participants (names of family members, children, or others present).
3. A short description of the service provided (e.g., supervised visit, parenting class, transport, etc.).
4. The date the visit or service took place, if it is mentioned in the notes. If no date is mentioned, say "unknown".

🧠 Guidelines:
- Write a detailed summary based on all available information. DO NOT shorten or leave out meaningful content.
- Do NOT fabricate or generalize.
- The summary should start like:  
  "On [extracted date or 'today'], the provider conducted a [visit/class/transport] for [family/client name]."

Here are the raw notes:
---
{input.content}
---

Respond ONLY in this JSON format:

{{
  "date": "...",
  "cleaned_summary": "...",
  "participants": "...",
  "visit_details": "..."
}}
"""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=700
        )

        response_text = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="AI response not in expected format.")

        return {
            "date": parsed["date"],
            "cleaned": parsed["cleaned_summary"],
            "participants": parsed["participants"],
            "visit_details": parsed["visit_details"]
        }

    except Exception as e:
        print("❌ GPT CLEAN ERROR:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI cleanup failed: {str(e)}")
