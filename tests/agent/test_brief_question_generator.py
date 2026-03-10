from dataclasses import dataclass

import pytest

from openpcb.agent.brief_question_generator import BriefQuestionGenerator
from openpcb.agent.llm.types import LLMError, LLMResponse
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


def test_brief_question_generator_success(monkeypatch) -> None:
    monkeypatch.setattr(
        "openpcb.agent.brief_question_generator.get_llm_client",
        lambda provider: _FakeClient("请确认输入电源范围？"),
    )
    generator = BriefQuestionGenerator()
    settings = AgentSettings(provider="deepseek", model="deepseek-chat", api_key="k", base_url="https://api.deepseek.com")
    text = generator.generate(
        settings=settings,
        board_class="mcu_core",
        board_family="stm32",
        current_field="power_input",
        field_label="输入电源",
        template_question="输入电源条件是什么？",
        options=["USB 5V", "12V", "电池"],
        filled_brief_summary={"board_goal": "控制板"},
        missing_fields=["power_input", "key_interfaces"],
    )
    assert text == "请确认输入电源范围？"


def test_brief_question_generator_failure_raises(monkeypatch) -> None:
    def _raise(provider):  # noqa: ANN001
        class _Client:
            def complete(self, request):  # noqa: ANN001
                raise LLMError("network error")

        _ = provider
        return _Client()

    monkeypatch.setattr("openpcb.agent.brief_question_generator.get_llm_client", _raise)
    generator = BriefQuestionGenerator()
    settings = AgentSettings(provider="deepseek", model="deepseek-chat", api_key="k", base_url="https://api.deepseek.com")
    with pytest.raises(LLMError):
        generator.generate(
            settings=settings,
            board_class="mcu_core",
            board_family="stm32",
            current_field="power_input",
            field_label="输入电源",
            template_question="输入电源条件是什么？",
            options=["USB 5V", "12V", "电池"],
            filled_brief_summary={"board_goal": "控制板"},
            missing_fields=["power_input", "key_interfaces"],
        )
