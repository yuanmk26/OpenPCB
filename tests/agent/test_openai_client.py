import io
import json
from urllib import error

import pytest

from openpcb.agent.llm.openai_client import OpenAIClient
from openpcb.agent.llm.types import LLMError, LLMRequest


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_openai_client_success(monkeypatch) -> None:
    def _fake_urlopen(req, timeout=30):  # noqa: ANN001
        _ = req
        _ = timeout
        return _FakeResponse(
            {
                "choices": [{"message": {"content": "{\"name\":\"demo\",\"requirements\":\"x\",\"modules\":[]}"}}],
                "usage": {"total_tokens": 123},
            }
        )

    monkeypatch.setattr("openpcb.agent.llm.openai_client.request.urlopen", _fake_urlopen)
    client = OpenAIClient()
    response = client.complete(
        LLMRequest(
            provider="openai",
            model="gpt-4o-mini",
            api_key="k",
            base_url="https://example.com",
            system_prompt="s",
            user_prompt="u",
        )
    )
    assert response.token_usage == 123
    assert "modules" in response.content


def test_openai_client_http_error(monkeypatch) -> None:
    def _fake_urlopen(req, timeout=30):  # noqa: ANN001
        _ = req
        _ = timeout
        raise error.HTTPError("https://example.com", 401, "unauthorized", hdrs=None, fp=io.BytesIO())

    monkeypatch.setattr("openpcb.agent.llm.openai_client.request.urlopen", _fake_urlopen)
    client = OpenAIClient()
    with pytest.raises(LLMError):
        client.complete(
            LLMRequest(
                provider="openai",
                model="gpt-4o-mini",
                api_key="k",
                base_url="https://example.com",
                system_prompt="s",
                user_prompt="u",
            )
        )
