import base64
import json

import httpx

from .config import settings


async def analyze_leaf_with_gemini(raw: bytes, mime_type: str) -> dict:
    """Ask Gemini for a cautious, image-based plant-health assessment."""
    if not settings.gemini_api_key:
        return {
            "status": "not_configured",
            "message": "Gemini AI is not configured. Add GEMINI_API_KEY to the backend environment.",
        }

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

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64.b64encode(raw).decode("ascii"),
                    },
                },
            ],
        }],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            headers={"x-goog-api-key": settings.gemini_api_key},
            json=payload,
        )

    try:
        body = response.json()
    except ValueError:
        body = {}

    if not response.is_success:
        provider_message = (
            body.get("error", {}).get("message")
            if isinstance(body.get("error"), dict)
            else None
        )
        detail = provider_message or response.text[:300] or "No provider details returned"
        raise RuntimeError(
            f"Gemini API returned HTTP {response.status_code}: {detail[:400]}"
        )

    candidates = body.get("candidates") or []
    if not candidates:
        feedback = body.get("promptFeedback") or {}
        reason = feedback.get("blockReason") or "The model returned no candidate response"
        raise RuntimeError(f"Gemini did not return an analysis: {reason}")

    parts = (candidates[0].get("content") or {}).get("parts") or []
    response_text = next(
        (part.get("text") for part in parts if isinstance(part.get("text"), str)),
        None,
    )
    if not response_text:
        finish_reason = candidates[0].get("finishReason", "unknown")
        raise RuntimeError(
            f"Gemini returned no readable analysis (finish reason: {finish_reason})"
        )

    try:
        result = json.loads(response_text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError("Gemini returned a response that was not valid JSON") from exc

    if not isinstance(result, dict):
        raise RuntimeError("Gemini returned an unexpected response format")

    if not result.get("is_leaf", False):
        return {
            "status": "not_a_leaf",
            "provider": "Google Gemini",
            "disease": "Image is not a clear leaf photo",
            "confidence": 0.0,
            "observations": str(
                result.get("observations", "Please upload a clear photo of one plant leaf.")
            ),
            "treatment": "Take a well-lit, close-up photo of a single leaf and try again.",
        }

    try:
        confidence = float(result.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    return {
        "status": "ok",
        "provider": "Google Gemini",
        "disease": str(result.get("disease", "Unable to identify")),
        "confidence": round(confidence, 3),
        "observations": str(result.get("observations", "")),
        "treatment": str(
            result.get("treatment", "Please consult a local agricultural expert.")
        ),
    }
