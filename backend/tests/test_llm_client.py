import pytest
from unittest.mock import patch, AsyncMock
from app.core.config import settings
from app.services.llm_client import (
    clean_json_response,
    resolve_provider_and_model,
    get_active_provider_label,
    call_llm
)

def test_clean_json_response_plain():
    raw = '{"score": 8.5, "reasoning": "High risk"}'
    assert clean_json_response(raw) == raw

def test_clean_json_response_markdown():
    raw = '```json\n{"score": 8.5, "reasoning": "High risk"}\n```'
    assert clean_json_response(raw) == '{"score": 8.5, "reasoning": "High risk"}'

def test_clean_json_response_generic_fence():
    raw = '```\n{"score": 8.5}\n```'
    assert clean_json_response(raw) == '{"score": 8.5}'

def test_resolve_provider_gemini():
    with patch.object(settings, "LLM_PROVIDER", "gemini"), \
         patch.object(settings, "GEMINI_API_KEY", "AIzaSyTestKey123456789"):
        provider, key, model = resolve_provider_and_model()
        assert provider == "gemini"
        assert key == "AIzaSyTestKey123456789"
        assert "gemini" in model

def test_resolve_provider_anthropic():
    with patch.object(settings, "LLM_PROVIDER", "anthropic"), \
         patch.object(settings, "ANTHROPIC_API_KEY", "sk-ant-testkey123456"):
        provider, key, model = resolve_provider_and_model()
        assert provider == "anthropic"
        assert key == "sk-ant-testkey123456"
        assert "claude" in model

def test_resolve_provider_auto():
    with patch.object(settings, "LLM_PROVIDER", "auto"), \
         patch.object(settings, "GEMINI_API_KEY", "AIzaSyTestKey123456789"), \
         patch.object(settings, "ANTHROPIC_API_KEY", ""):
        provider, key, _ = resolve_provider_and_model()
        assert provider == "gemini"
        assert key == "AIzaSyTestKey123456789"

def test_resolve_provider_fallback():
    with patch.object(settings, "LLM_PROVIDER", "auto"), \
         patch.object(settings, "GEMINI_API_KEY", ""), \
         patch.object(settings, "ANTHROPIC_API_KEY", ""):
        provider, key, model = resolve_provider_and_model()
        assert provider == "fallback"
        assert get_active_provider_label() == "Calibrated Deterministic Reasoning Engine (Offline)"

@pytest.mark.asyncio
async def test_call_llm_fallback_when_unconfigured():
    with patch.object(settings, "GEMINI_API_KEY", ""), \
         patch.object(settings, "ANTHROPIC_API_KEY", ""):
        res, inp, outp = await call_llm(
            system_prompt="System instructions",
            user_prompt="Evaluate risk",
            json_mode=True
        )
        assert res is None
        assert inp > 0
        assert outp == 80

@pytest.mark.asyncio
async def test_call_gemini_mocked():
    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": '{"score": 9.0, "reasoning": "High AML risk"}'}]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 42,
            "candidatesTokenCount": 18
        }
    }

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: mock_gemini_response

    with patch.object(settings, "LLM_PROVIDER", "gemini"), \
         patch.object(settings, "GEMINI_API_KEY", "AIzaSyValidTestKey123"), \
         patch("httpx.AsyncClient.post", return_value=mock_resp):
        res, inp, outp = await call_llm(
            system_prompt="System",
            user_prompt="Analyze this case",
            json_mode=True
        )
        assert res == {"score": 9.0, "reasoning": "High AML risk"}
        assert inp == 42
        assert outp == 18
