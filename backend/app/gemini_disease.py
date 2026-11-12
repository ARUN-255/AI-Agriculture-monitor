import json
import re

import httpx

from .config import settings


async def analyze_leaf_with_gemini(raw: bytes, mime_type: str) -> dict:
    """Ask Gemini for a cautious, image-based plant-health assessment."""
    if not settings.gemini_api_key:
        return {"status": "not_configured", "message": "Gemini AI is not configured yet. Add GEMINI_API_KEY to the backend environment."}

    prompt = """
You are a cautious plant-health assistant for a farming demonstration.
Inspect the supplied image. First decide whether it clearly shows a plant leaf.
Do not claim certainty. Do not invent details that cannot be seen.
Return ONLY valid JSON with these keys:
{
  "is_leaf": true,
  "disease": "short possible disease name or 'No obvious disease visible'",
  "confidence": 0.0,
  "observations": "short description of visible signs",
  "treatment": "low-risk practical next steps"
}
If the image is not a plant leaf, set is_leaf to false, disease to "Image is not a clear leaf photo", confidence to 0, and explain this in observations.
Confidence must be a number from 0 to 1 and is an AI estimate, not a scientifically calibrated probability.
Do not recommend chemical brands, pesticide doses, or unsafe treatments. Recommend confirmation by a local agricultural expert before applying chemicals.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": mime_type, "data": __import__("base64").b64encode(raw).decode("ascii")}}
            ]
        }],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, headers={"x-goog-api-key": settings.gemini_api_key}, json=payload)
            response.raise_for_status()
            body = response.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Gemini returned an unreadable result")
        result = json.loads(match.group(0))
        if not result.get("is_leaf", False):
            return {
                "status": "not_a_leaf",
                "provider": "Google Gemini",
                "disease": "Image is not a clear leaf photo",
                "confidence": 0.0,
                "observations": str(result.get("observations", "Please upload a clear photo of one plant leaf.")),
                "treatment": "Take a well-lit, close-up photo of a single leaf and try again."
            }
        confidence = float(result.get("confidence", 0))
        confidence = max(0.0, min(1.0, confidence))
        return {
            "status": "ok",
            "provider": "Google Gemini",
            "disease": str(result.get("disease", "Unable to identify")),
            "confidence": round(confidence, 3),
            "observations": str(result.get("observations", "")),
            "treatment": str(result.get("treatment", "Please consult a local agricultural expert."))
        }
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (400, 401, 403):
            raise RuntimeError("Gemini rejected the request. Check the GEMINI_API_KEY and model setting.") from exc
        raise RuntimeError(f"Gemini service returned HTTP {exc.response.status_code}. Try again later.") from exc
    except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError) as exc:
        raise RuntimeError("Gemini could not analyze this image. Please try a clear JPG, PNG or WEBP leaf photo.") from exc
