from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openpcb.config.settings import Settings


class LLMClientError(Exception):
    """
    Base exception for LLM client errors.
    """


class LLMConfigurationError(LLMClientError):
    """
    Raised when the LLM client is misconfigured.
    """


class LLMResponseError(LLMClientError):
    """
    Raised when the LLM provider returns an unusable response.
    """


@dataclass(slots=True)
class LLMRequest:
    """
    A normalized request object for LLM calls.
    """

    system_prompt: str
    user_prompt: str
    temperature: float | None = None
    response_format: dict[str, Any] | None = None


@dataclass(slots=True)
class LLMResponse:
    """
    A normalized response object returned by the LLM client.
    """

    content: str
    raw: Any | None = None
    model: str | None = None


class LLMClient:
    """
    Minimal LLM client abstraction for OpenPCB.

    This class intentionally provides a small, stable interface so the rest
    of the application does not depend directly on any specific SDK.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider = settings.llm_provider.strip().lower()
        self._model = settings.llm_model.strip()

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """
        Generate a completion from the configured LLM provider.

        Args:
            system_prompt: High-level system instruction.
            user_prompt: Task-specific user content.
            temperature: Optional override for sampling temperature.
            response_format: Optional structured-output hint/schema.

        Returns:
            LLMResponse: normalized model output.

        Raises:
            LLMConfigurationError: if required settings are missing.
            LLMClientError: if the provider is unsupported or request fails.
            LLMResponseError: if the provider returns an invalid response.
        """
        request = LLMRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            response_format=response_format,
        )
        return self._dispatch(request)

    def _dispatch(self, request: LLMRequest) -> LLMResponse:
        """
        Route the request to the configured provider implementation.
        """
        if self._provider == "openai":
            return self._generate_with_openai(request)

        raise LLMConfigurationError(
            f"Unsupported LLM provider: {self._provider!r}"
        )

    def _generate_with_openai(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response using the OpenAI Python SDK.

        Notes:
            - This implementation uses a small compatibility layer.
            - The rest of the application never talks to the SDK directly.
            - If you later switch SDK versions, changes stay localized here.
        """
        if not self._settings.has_llm_api_key:
            raise LLMConfigurationError(
                "Missing LLM API key. Please set LLM_API_KEY in your environment."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMConfigurationError(
                "The 'openai' package is not installed. Please add it to your project dependencies."
            ) from exc

        client_kwargs: dict[str, Any] = {
            "api_key": self._settings.llm_api_key,
            "timeout": self._settings.llm_timeout_seconds,
        }
        if self._settings.llm_base_url:
            client_kwargs["base_url"] = self._settings.llm_base_url

        try:
            client = OpenAI(**client_kwargs)

            messages = [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ]

            create_kwargs: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "temperature": (
                    request.temperature
                    if request.temperature is not None
                    else self._settings.llm_temperature
                ),
            }

            if request.response_format is not None:
                create_kwargs["response_format"] = request.response_format

            raw_response = client.chat.completions.create(**create_kwargs)
        except Exception as exc:
            raise LLMClientError(f"OpenAI request failed: {exc}") from exc

        try:
            choice = raw_response.choices[0]
            message = choice.message
            content = message.content
        except Exception as exc:
            raise LLMResponseError(
                "OpenAI returned an unexpected response structure."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMResponseError("OpenAI returned empty response content.")

        return LLMResponse(
            content=content,
            raw=raw_response,
            model=getattr(raw_response, "model", self._model),
        )