from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.auth_dependencies import get_current_user
import openai
import os

router = APIRouter()

class NoteInput(BaseModel):
    content: str

@router.post("/ai/clean-note")
async def clean_note(input: NoteInput, user=Depends(get_current_user)):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        prompt = f"""
        Rewrite the following field note to sound professional, clear, and grammatically correct.
        Do not change the meaning or remove any important details.
        ---
        {input.content}
        ---
        """

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400
        )

        cleaned = response.choices[0].message.content.strip()
        return {"cleaned": cleaned}
    except Exception as e:
        print("❌ GPT CLEAN ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"AI cleanup failed: {str(e)}")
