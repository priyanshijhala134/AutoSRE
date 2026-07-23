import json
import os
import re

from google import genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def llm_available() -> bool:
    return bool(GOOGLE_API_KEY)


def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> dict:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set")

    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(model=model, contents=prompt)
    text = response.text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

    return json.loads(text)
