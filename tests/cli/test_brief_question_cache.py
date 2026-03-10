from pathlib import Path

from openpcb.agent.brief_collector import ArchitectureBriefCollector
from openpcb.agent.session import ChatSession
from openpcb.cli.commands.chat import _resolve_brief_question_text
from openpcb.config.settings import AgentSettings


def test_resolve_brief_question_text_uses_cache(monkeypatch, tmp_path: Path) -> None:
    session = ChatSession.create(project_dir=tmp_path / "demo")
    session.architecture_brief = {"board_goal": "控制板"}

    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        brief=session.architecture_brief,
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    classification = {"board_class": "mcu_core", "board_family": "stm32"}

    monkeypatch.setattr(
        "openpcb.cli.commands.chat.load_agent_settings",
        lambda config_path, overrides: AgentSettings(  # noqa: ARG005
            provider="deepseek",
            model="deepseek-chat",
            api_key="k",
            base_url="https://api.deepseek.com",
        ),
    )
    call_count = {"n": 0}

    class _FakeGenerator:
        def generate(self, **kwargs):  # noqa: ANN003
            _ = kwargs
            call_count["n"] += 1
            return "动态提问"

    monkeypatch.setattr("openpcb.cli.commands.chat.BriefQuestionGenerator", lambda: _FakeGenerator())

    q1 = _resolve_brief_question_text(
        session,
        collector=collector,
        classification=classification,
        result_question=result.template_question or "",
        current_field=str(result.current_field),
        options=result.options,
        missing_fields=result.missing_fields,
        template_id=result.template_id,
        config=Path("openpcb.config.toml"),
        provider="deepseek",
        model="deepseek-chat",
    )
    q2 = _resolve_brief_question_text(
        session,
        collector=collector,
        classification=classification,
        result_question=result.template_question or "",
        current_field=str(result.current_field),
        options=result.options,
        missing_fields=result.missing_fields,
        template_id=result.template_id,
        config=Path("openpcb.config.toml"),
        provider="deepseek",
        model="deepseek-chat",
    )
    assert q1 == "动态提问"
    assert q2 == "动态提问"
    assert call_count["n"] == 1


def test_resolve_brief_question_text_fallback_on_error(monkeypatch, tmp_path: Path) -> None:
    session = ChatSession.create(project_dir=tmp_path / "demo")
    collector = ArchitectureBriefCollector()
    result = collector.collect(
        board_class="mcu_core",
        board_family="stm32",
        user_text="",
        brief={},
        pending_field=None,
        pending_options=None,
        expect_custom_input=False,
    )
    classification = {"board_class": "mcu_core", "board_family": "stm32"}

    def _raise(*args, **kwargs):  # noqa: ANN002, ANN003
        _ = (args, kwargs)
        raise RuntimeError("boom")

    monkeypatch.setattr("openpcb.cli.commands.chat.load_agent_settings", _raise)
    fallback = _resolve_brief_question_text(
        session,
        collector=collector,
        classification=classification,
        result_question=result.template_question or "",
        current_field=str(result.current_field),
        options=result.options,
        missing_fields=result.missing_fields,
        template_id=result.template_id,
        config=Path("openpcb.config.toml"),
        provider="deepseek",
        model="deepseek-chat",
    )
    assert fallback == (result.template_question or "")
