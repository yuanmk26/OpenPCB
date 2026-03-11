from dataclasses import dataclass

import pytest

from openpcb.agent.llm.types import LLMError, LLMResponse
from openpcb.agent.schema_question_generator import SchemaQuestionGenerator
from openpcb.config.settings import AgentSettings


@dataclass
class _FakeClient:
    content: str

    def complete(self, request):  # noqa: ANN001
        _ = request
        return LLMResponse(
            provider="deepseek",
            model="deepseek-chat",
            content=self.content,
            token_usage=10,
            latency_ms=5,
            raw_response={},
        )


def test_schema_question_generator_success(monkeypatch) -> None:
    monkeypatch.setattr(
        "openpcb.agent.schema_question_generator.get_llm_client",
        lambda provider: _FakeClient("????????"),
    )
    gen = SchemaQuestionGenerator()
    settings = AgentSettings(provider="deepseek", model="deepseek-chat", api_key="k", base_url="https://api.deepseek.com")
    text = gen.generate(
        settings=settings,
        board_class="mcu_core",
        board_family="stm32",
        field_key="main_controller_part",
        field_label="????",
        question_seed="????????",
        options=["STM32F103", "STM32F407", "STM32H743"],
        missing_fields=["main_controller_part"],
        confirmed_fields={"board_type": "MCU ???"},
        inferred_fields={"main_controller_type": "STM32"},
    )
    assert text == "????????"


def test_schema_question_generator_failure_raises(monkeypatch) -> None:
    def _raise(provider):  # noqa: ANN001
        class _Client:
            def complete(self, request):  # noqa: ANN001
                raise LLMError("network error")

        _ = provider
        return _Client()

    monkeypatch.setattr("openpcb.agent.schema_question_generator.get_llm_client", _raise)
    gen = SchemaQuestionGenerator()
    settings = AgentSettings(provider="deepseek", model="deepseek-chat", api_key="k", base_url="https://api.deepseek.com")
    with pytest.raises(LLMError):
        gen.generate(
            settings=settings,
            board_class="mcu_core",
            board_family="stm32",
            field_key="main_controller_part",
            field_label="????",
            question_seed="????????",
            options=["STM32F103", "STM32F407", "STM32H743"],
            missing_fields=["main_controller_part"],
            confirmed_fields={},
            inferred_fields={},
        )
