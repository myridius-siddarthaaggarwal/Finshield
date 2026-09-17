"""
FinShield Multi-Provider LLM Client
Unified interface supporting Google Gemini (Gemini 1.5 Pro, 2.5 Pro, Flash)
and Anthropic Claude (Claude 3.7 Sonnet) with automatic provider resolution,
JSON schema enforcement, token telemetry, and seamless offline fallback.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, Tuple
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


def clean_json_response(raw_text: str) -> str:
    """
    Strips markdown code fences (```json ... ```) or trailing text
    to extract a clean JSON payload.
    """
    text = raw_text.strip()
    # Match ```json <content> ``` or ``` <content> ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return text


def resolve_provider_and_model() -> Tuple[str, str, str]:
    """
    Resolves the active LLM provider, API key, and model identifier
    based on settings and available API keys.
    Returns: (provider, api_key, model) where provider is 'gemini', 'anthropic', or 'fallback'.
    """
    provider_pref = (settings.LLM_PROVIDER or "auto").strip().lower()

    # Explicit Gemini request
    if provider_pref == "gemini":
        key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
        if len(key) > 5:
            model = settings.LLM_MODEL if "gemini" in settings.LLM_MODEL.lower() else "gemini-1.5-pro"
            return "gemini", key, model
        logger.warning("LLM_PROVIDER is set to 'gemini' but GEMINI_API_KEY is missing or invalid.")
        return "fallback", "", ""

    # Explicit Anthropic request
    if provider_pref == "anthropic":
        key = settings.ANTHROPIC_API_KEY.strip() if settings.ANTHROPIC_API_KEY else ""
        if len(key) > 5:
            model = settings.LLM_MODEL if "claude" in settings.LLM_MODEL.lower() else "claude-3-7-sonnet-20250219"
            return "anthropic", key, model
        logger.warning("LLM_PROVIDER is set to 'anthropic' but ANTHROPIC_API_KEY is missing or invalid.")
        return "fallback", "", ""

    # Auto-detect: prioritize Gemini if GEMINI_API_KEY provided, otherwise Anthropic
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5:
        model = settings.LLM_MODEL if "gemini" in settings.LLM_MODEL.lower() else "gemini-1.5-pro"
        return "gemini", settings.GEMINI_API_KEY.strip(), model

    if settings.ANTHROPIC_API_KEY and len(settings.ANTHROPIC_API_KEY.strip()) > 5:
        model = settings.LLM_MODEL if "claude" in settings.LLM_MODEL.lower() else "claude-3-7-sonnet-20250219"
        return "anthropic", settings.ANTHROPIC_API_KEY.strip(), model

    return "fallback", "", ""


def get_active_provider_label() -> str:
    """Returns a user-friendly label of the active AI reasoning provider."""
    provider, _, model = resolve_provider_and_model()
    if provider == "gemini":
        return f"Google Gemini ({model})"
    if provider == "anthropic":
        return f"Anthropic Claude ({model})"
    return "Calibrated Deterministic Reasoning Engine (Offline)"


async def _call_gemini_api(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
    timeout: float
) -> Tuple[str, int, int]:
    """Invokes Google Gemini REST API generateContent endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    generation_config: Dict[str, Any] = {
        "temperature": temperature,
        "maxOutputTokens": max_tokens,
    }
    if json_mode:
        generation_config["responseMimeType"] = "application/json"

    payload: Dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}]
            }
        ],
        "generationConfig": generation_config
    }

    if system_prompt:
        payload["systemInstruction"] = {
            "parts": [{"text": system_prompt}]
        }

    async with httpx.AsyncClient(timeout=timeout) as client:
        res = await client.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            raise RuntimeError(f"Gemini API returned HTTP {res.status_code}: {res.text}")

        data = res.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Gemini returned no response candidates: {data}")

        raw_text = candidates[0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        inp_tokens = usage.get("promptTokenCount", len((system_prompt + " " + user_prompt).split()) * 2)
        outp_tokens = usage.get("candidatesTokenCount", len(raw_text.split()) * 2)

        return raw_text, inp_tokens, outp_tokens


async def _call_anthropic_api(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    timeout: float
) -> Tuple[str, int, int]:
    """Invokes Anthropic Claude Messages REST API."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    if system_prompt:
        payload["system"] = system_prompt

    async with httpx.AsyncClient(timeout=timeout) as client:
        res = await client.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            raise RuntimeError(f"Anthropic API returned HTTP {res.status_code}: {res.text}")

        data = res.json()
        raw_text = data["content"][0]["text"]
        usage = data.get("usage", {})
        inp_tokens = usage.get("input_tokens", len((system_prompt + " " + user_prompt).split()) * 2)
        outp_tokens = usage.get("output_tokens", len(raw_text.split()) * 2)

        return raw_text, inp_tokens, outp_tokens


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 256,
    temperature: Optional[float] = None,
    json_mode: bool = True,
    timeout: float = 12.0
) -> Tuple[Optional[Any], int, int]:
    """
    Unified LLM call supporting Gemini Pro and Claude with fallback.
    Returns: (parsed_result_or_raw_text, input_tokens, output_tokens)
    If no API key is available or the call fails, returns (None, est_input_tokens, est_output_tokens).
    """
    temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    est_input = len((system_prompt + " " + user_prompt).split())
    est_output = 80

    provider, api_key, model = resolve_provider_and_model()

    if provider == "fallback":
        return None, est_input, est_output

    try:
        if provider == "gemini":
            raw_text, inp, outp = await _call_gemini_api(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temp,
                json_mode=json_mode,
                timeout=timeout
            )
        elif provider == "anthropic":
            raw_text, inp, outp = await _call_anthropic_api(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temp,
                timeout=timeout
            )
        else:
            return None, est_input, est_output

        if json_mode:
            cleaned = clean_json_response(raw_text)
            parsed = json.loads(cleaned)
            return parsed, inp, outp
        return raw_text, inp, outp

    except Exception as e:
        logger.warning(f"Live LLM call to {provider} ({model}) failed ({e}). Reverting to calibrated fallback.")
        return None, est_input, est_output
