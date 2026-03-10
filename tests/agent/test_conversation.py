from openpcb.agent.conversation import decide_action
from openpcb.agent.models import AgentTaskType


def test_decide_action_routes_plan_when_no_project() -> None:
    decision = decide_action("design stm32 with usb", has_project=False)
    assert decision.action_route == AgentTaskType.PLAN
    assert decision.requires_confirmation is False


def test_decide_action_routes_check_without_confirmation() -> None:
    decision = decide_action("please check power risk", has_project=True)
    assert decision.action_route == AgentTaskType.CHECK
    assert decision.requires_confirmation is False


def test_decide_action_routes_edit_with_confirmation() -> None:
    decision = decide_action("add one more led", has_project=True)
    assert decision.action_route == AgentTaskType.EDIT
    assert decision.requires_confirmation is True
    assert decision.payload == "add one more led"


def test_decide_action_clarifies_when_ambiguous() -> None:
    decision = decide_action("tell me more", has_project=True)
    assert decision.action_route is None
    assert decision.clarification is not None
