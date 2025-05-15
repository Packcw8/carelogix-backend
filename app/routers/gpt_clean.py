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
        You are a documentation assistant helping a family services provider summarize supervised visits, transports, and skill-based services (e.g., Adult Life Skills, Parenting Classes).

        The input consists of:
        - Line 1: the date (e.g., May 25, 2025)
        - Line 2: the type of service (e.g., SV1, ATT, Transport, Skill Building, Class)
        - Line 3 and onward: raw infield notes describing the provider's actions and observations

        Your task is to extract:
        1. A professional, third-person summary that starts with the date and clearly states what occurred.
        2. The names of any participants mentioned.
        3. The type of service provided (copied from line 2).
        4. The visit date (copied from line 1).

        🧠 Guidelines:
        - Refer to the provider as “the provider”
        - Write in full sentences
        - Do NOT fabricate or assume anything
        - Use the actual wording where possible
        - Always respect the formatting of the raw notes

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
