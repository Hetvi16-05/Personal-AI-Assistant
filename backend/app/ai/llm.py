
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

_model = genai.GenerativeModel("gemini-2.5-flash")


def ask_llm(prompt: str, system_hint: str = "") -> str:
    """
    Send a prompt to Gemini and return the text response.
    system_hint is prepended as context if provided.
    """
    full_prompt = f"{system_hint}\n\n{prompt}".strip() if system_hint else prompt
    response = _model.generate_content(full_prompt)
    return response.text.strip()
