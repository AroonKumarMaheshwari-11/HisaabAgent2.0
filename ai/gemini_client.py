"""
Single wrapped Gemini client. Every AI call in the app goes through here so
retry logic, error handling, and API-key resolution exist in exactly one
place.
"""

import json
import os
import time
import traceback
from typing import Optional

from config import (
    GEMINI_MODEL, GEMINI_API_KEY_ENV_VAR, GEMINI_MAX_RETRIES,
    GEMINI_TEMPERATURE_EXTRACTION, GEMINI_TEMPERATURE_ANALYSIS,
)

FRIENDLY_ERROR = (
    "HisaabAgent couldn't reach the AI service just now. "
    "Please check your connection and try again."
)

# Substrings of errors that retrying will never fix.
_PERMANENT_ERROR_HINTS = (
    "404", "NOT_FOUND", "400", "INVALID_ARGUMENT",
    "401", "403", "PERMISSION_DENIED", "API key not valid",
)


class GeminiError(Exception):
    """Raised for any Gemini failure the UI should show a friendly message for."""
    pass


def _get_api_key() -> Optional[str]:
    """
    Resolution order: environment variable (local dev) then Streamlit
    secrets (deployed). Imports streamlit lazily so this module stays
    importable in non-Streamlit contexts (tests, scripts).
    """
    key = os.environ.get(GEMINI_API_KEY_ENV_VAR)
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("gemini", {}).get("api_key")
    except Exception:
        return None


def _get_client():
    api_key = _get_api_key()
    if not api_key:
        raise GeminiError(
            "Gemini API key not configured. Set the GEMINI_API_KEY environment "
            "variable locally, or add it to Streamlit secrets when deployed."
        )
    try:
        from google import genai
    except ImportError as e:
        raise GeminiError(
            "The google-genai package is not installed. Run: "
            "pip install google-genai"
        ) from e
    return genai.Client(api_key=api_key)


def _log_error(where: str, error: Exception) -> None:
    """Prints the real error to the terminal so it can be diagnosed."""
    print(f"\n[GEMINI ERROR in {where}] model={GEMINI_MODEL}", flush=True)
    print(f"{type(error).__name__}: {error}", flush=True)
    traceback.print_exc()


def _is_permanent(error: Exception) -> bool:
    text = f"{type(error).__name__} {error}"
    return any(hint in text for hint in _PERMANENT_ERROR_HINTS)


def generate_json(prompt: str, response_schema: dict, temperature: float = None) -> dict:
    """
    Calls Gemini with a JSON-schema-constrained response. Retries on
    transient failures. Raises GeminiError with a friendly message on
    final failure - callers should catch this and show it, never a raw
    traceback.
    """
    from google.genai import types

    client = _get_client()
    temp = temperature if temperature is not None else GEMINI_TEMPERATURE_EXTRACTION

    last_error = None
    for attempt in range(GEMINI_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temp,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            last_error = e
            _log_error("generate_json (bad JSON)", e)
            time.sleep(0.5)
            continue
        except Exception as e:
            last_error = e
            _log_error("generate_json", e)
            if _is_permanent(e):
                break
            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(1.0 * (attempt + 1))
                continue
            break

    raise GeminiError(FRIENDLY_ERROR) from last_error


def generate_text(prompt: str, temperature: float = None) -> str:
    """Plain text generation for narrative insights (no JSON schema needed)."""
    from google.genai import types

    client = _get_client()
    temp = temperature if temperature is not None else GEMINI_TEMPERATURE_ANALYSIS

    last_error = None
    for attempt in range(GEMINI_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temp),
            )
            return (response.text or "").strip()
        except Exception as e:
            last_error = e
            _log_error("generate_text", e)
            if _is_permanent(e):
                break
            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(1.0 * (attempt + 1))
                continue
            break

    raise GeminiError(FRIENDLY_ERROR) from last_error


def is_configured() -> bool:
    """Cheap check for whether an API key is present - used for the
    sidebar 'AI Online' indicator without making a real API call each rerun."""
    return _get_api_key() is not None