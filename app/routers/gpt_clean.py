from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.auth_dependencies import get_current_user
import openai
import os
import traceback



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
        You are a documentation assistant helping a family services provider summarize a supervised visit.

        Based on the raw notes provided below, create a professional, detailed summary written in the third person. 
        Refer to the writer as “the provider.” Focus on family interactions, atmosphere, behavior of the children, and any notable dialogue or context.
        Make the summary sound like a well-written paragraph used in a visit report.

        DO NOT leave out meaningful content. DO NOT summarize with generalities if specific information is present.

        Begin the summary with a sentence like: 
        "On [today’s date or the one in the note], the provider conducted a supervised visit for [family name if available]."

        Here are the raw notes:
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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI cleanup failed: {str(e)}")
