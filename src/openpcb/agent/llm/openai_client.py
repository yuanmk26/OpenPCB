"""OpenAI chat completions client."""

from __future__ import annotations

import json
from time import perf_counter
from urllib.parse import urlparse, urlunparse
from urllib import error, request

from openpcb.agent.llm.base import LLMClient
from openpcb.agent.llm.types import LLMError, LLMRequest, LLMResponse


class OpenAIClient(LLMClient):
    """Minimal OpenAI-compatible client via stdlib urllib."""

    def complete(self, llm_request: LLMRequest) -> LLMResponse:
        endpoint = _normalize_chat_completions_url(llm_request.base_url)
        payload = {
            "model": llm_request.model,
            "messages": llm_request.messages
            or [
                {"role": "system", "content": llm_request.system_prompt},
                {"role": "user", "content": llm_request.user_prompt},
            ],
            "temperature": 0.2,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {llm_request.api_key}",
            },
            method="POST",
        )

        last_error: LLMError | None = None
        for _ in range(llm_request.max_retries + 1):
            started = perf_counter()
            try:
                with request.urlopen(req, timeout=llm_request.timeout) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                latency = int((perf_counter() - started) * 1000)
                content = raw["choices"][0]["message"]["content"]
                usage = raw.get("usage", {}).get("total_tokens")
                return LLMResponse(
                    provider=llm_request.provider,
                    model=llm_request.model,
                    content=content,
                    token_usage=usage,
                    latency_ms=latency,
                    raw_response=raw,
                )
            except error.HTTPError as exc:
                code = getattr(exc, "code", None)
                last_error = LLMError(
                    f"{llm_request.provider} HTTP error: {code} endpoint={endpoint}",
                    code=code,
                )
            except (error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
                last_error = LLMError(f"{llm_request.provider} request failed: {exc} endpoint={endpoint}")
        if last_error is None:
            last_error = LLMError(f"{llm_request.provider} request failed with unknown error. endpoint={endpoint}")
        raise last_error


def _normalize_chat_completions_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        return base_url
    normalized_path = parsed.path.rstrip("/")
    if normalized_path.endswith("/chat/completions"):
        return base_url.rstrip("/")
    if normalized_path in {"", "/"}:
        normalized_path = "/chat/completions"
    else:
        normalized_path = f"{normalized_path}/chat/completions"
    return urlunparse((parsed.scheme, parsed.netloc, normalized_path, parsed.params, parsed.query, parsed.fragment))
