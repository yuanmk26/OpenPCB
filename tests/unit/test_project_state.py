from __future__ import annotations

from openpcb.domain.project.state import (
    PlannerAction,
    PlannerDecision,
    ProjectStage,
    ProjectState,
    ProjectStatus,
)
from openpcb.domain.requirements.models import BoardType, RequirementSpec


def test_create_initial_project_state() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    assert state.project_id == "project-001"
    assert state.stage == ProjectStage.INIT
    assert state.status == ProjectStatus.IDLE
    assert state.conversation.session_id == "session-001"
    assert state.conversation.turn_count == 0
    assert state.requirement_spec is None
    assert state.has_requirements is False


def test_record_user_message_updates_conversation_state() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    state.record_user_message("I want an STM32 minimum system board.")

    assert state.conversation.turn_count == 1
    assert state.conversation.last_user_message == "I want an STM32 minimum system board."


def test_record_agent_message_updates_conversation_state() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    state.record_agent_message("What power input do you want?")

    assert state.conversation.last_agent_message == "What power input do you want?"


def test_apply_requirement_spec_with_missing_fields_moves_to_clarification() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        known_missing_fields=["power_input", "mcu.family"],
        clarification_questions=[
            "How is the board powered?",
            "Which MCU family do you want?",
        ],
    )

    state.apply_requirement_spec(spec)

    assert state.requirement_spec is spec
    assert state.stage == ProjectStage.REQUIREMENT_CLARIFICATION
    assert state.status == ProjectStatus.WAITING_FOR_USER
    assert state.missing_fields == ["power_input", "mcu.family"]
    assert state.open_questions == [
        "How is the board powered?",
        "Which MCU family do you want?",
    ]
    assert state.has_requirements is True
    assert state.is_waiting_for_user is True


def test_apply_requirement_spec_without_missing_fields_stays_active() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    spec = RequirementSpec(
        board_type=BoardType.MCU_MINIMUM_SYSTEM,
        known_missing_fields=[],
        clarification_questions=[],
    )

    state.apply_requirement_spec(spec)

    assert state.stage == ProjectStage.REQUIREMENT_COLLECTION
    assert state.status == ProjectStatus.ACTIVE
    assert state.missing_fields == []
    assert state.open_questions == []


def test_apply_planner_decision_for_clarification() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    decision = PlannerDecision(
        next_action=PlannerAction.ASK_USER_FOR_CLARIFICATION,
        target_stage=ProjectStage.REQUIREMENT_CLARIFICATION,
        reason="power input missing",
        missing_fields=["power_input"],
        clarification_questions=["How is the board powered?"],
    )

    state.apply_planner_decision(decision)

    assert state.last_planner_decision == decision
    assert state.stage == ProjectStage.REQUIREMENT_CLARIFICATION
    assert state.status == ProjectStatus.WAITING_FOR_USER
    assert state.missing_fields == ["power_input"]
    assert state.open_questions == ["How is the board powered?"]


def test_apply_planner_decision_for_failure() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    decision = PlannerDecision(
        next_action=PlannerAction.FAIL_PROJECT,
        target_stage=ProjectStage.ERROR,
        reason="llm parsing failed repeatedly",
    )

    state.apply_planner_decision(decision)

    assert state.stage == ProjectStage.ERROR
    assert state.status == ProjectStatus.FAILED
    assert "llm parsing failed repeatedly" in state.errors


def test_mark_completed() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    state.mark_completed()

    assert state.stage == ProjectStage.COMPLETED
    assert state.status == ProjectStatus.DONE


def test_mark_error() -> None:
    state = ProjectState.create_initial(
        project_id="project-001",
        session_id="session-001",
    )

    state.mark_error("unexpected runtime error")

    assert state.stage == ProjectStage.ERROR
    assert state.status == ProjectStatus.FAILED
    assert "unexpected runtime error" in state.errors