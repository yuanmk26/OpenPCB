from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from openpcb.domain.requirements.models import RequirementSpec


def utc_now() -> datetime:
    """
    Return a timezone-aware UTC timestamp.
    """
    return datetime.now(timezone.utc)


class ProjectStage(str, Enum):
    """
    High-level lifecycle stage of an OpenPCB project.

    The project should move forward stage by stage, but it may also move
    backward if newly discovered information invalidates earlier assumptions.
    """

    INIT = "init"
    REQUIREMENT_COLLECTION = "requirement_collection"
    REQUIREMENT_CLARIFICATION = "requirement_clarification"
    ARCHITECTURE_DESIGN = "architecture_design"
    SCHEMATIC_PLANNING = "schematic_planning"
    REVIEW = "review"
    COMPLETED = "completed"
    ERROR = "error"


class ProjectStatus(str, Enum):
    """
    Coarse execution status of the project runtime.
    """

    IDLE = "idle"
    ACTIVE = "active"
    WAITING_FOR_USER = "waiting_for_user"
    BLOCKED = "blocked"
    FAILED = "failed"
    DONE = "done"


class PlannerAction(str, Enum):
    """
    Normalized action names that planner/orchestrator can exchange.

    These actions are intentionally explicit so that the decision process is
    observable and testable, instead of being hidden in free-form text.
    """

    ASK_USER_FOR_CLARIFICATION = "ask_user_for_clarification"
    RUN_REQUIREMENT_EXTRACTION = "run_requirement_extraction"
    RUN_ARCHITECTURE_FLOW = "run_architecture_flow"
    RUN_SCHEMATIC_PLANNING = "run_schematic_planning"
    VALIDATE_CURRENT_STATE = "validate_current_state"
    COMPLETE_STAGE = "complete_stage"
    FAIL_PROJECT = "fail_project"


class PlannerDecision(BaseModel):
    """
    Structured result of one planner decision.

    This object is not the whole project state; it is the planner's most recent
    conclusion about what the system should do next.
    """

    model_config = ConfigDict(extra="forbid")

    next_action: PlannerAction = Field(
        ...,
        description="The next action chosen by the planner.",
    )
    target_stage: ProjectStage | None = Field(
        default=None,
        description="Stage the system expects to enter or remain in.",
    )
    reason: str | None = Field(
        default=None,
        description="Short machine-readable or human-readable reason for the decision.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Requirement field paths that are still missing.",
    )
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Suggested questions to ask the user next.",
    )


class ConversationState(BaseModel):
    """
    Minimal conversation-related state for one project session.

    This keeps only the information that is immediately useful for the MVP.
    """

    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(
        ...,
        description="Session identifier used by the runtime.",
    )
    turn_count: int = Field(
        default=0,
        ge=0,
        description="How many user turns have been processed in this session.",
    )
    last_user_message: str | None = Field(
        default=None,
        description="Most recent raw user message.",
    )
    last_agent_message: str | None = Field(
        default=None,
        description="Most recent agent-visible reply.",
    )


class ProjectState(BaseModel):
    """
    The central mutable state object for an OpenPCB project.

    This is the main IR-like runtime snapshot used by planner, orchestrator,
    and services. It should answer these questions clearly:

    - What project are we working on?
    - Which stage are we in?
    - What requirements do we currently know?
    - What is still missing?
    - What did the planner decide most recently?
    """

    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(
        ...,
        description="Stable identifier for the current project.",
    )

    stage: ProjectStage = Field(
        default=ProjectStage.INIT,
        description="Current lifecycle stage.",
    )
    status: ProjectStatus = Field(
        default=ProjectStatus.IDLE,
        description="Current coarse runtime status.",
    )

    conversation: ConversationState = Field(
        ...,
        description="Conversation/session-related runtime state.",
    )

    requirement_spec: RequirementSpec | None = Field(
        default=None,
        description="Current structured requirement specification if available.",
    )

    last_planner_decision: PlannerDecision | None = Field(
        default=None,
        description="The most recent planner output.",
    )

    open_questions: list[str] = Field(
        default_factory=list,
        description="Questions that still need user answers.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Normalized requirement field paths still missing.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings accumulated during processing.",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Fatal or semi-fatal errors accumulated during processing.",
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        description="Project state creation timestamp in UTC.",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        description="Last update timestamp in UTC.",
    )

    def touch(self) -> None:
        """
        Update the state's modification timestamp.
        """
        self.updated_at = utc_now()

    def record_user_message(self, message: str) -> None:
        """
        Update conversation state when a new user message is received.
        """
        self.conversation.turn_count += 1
        self.conversation.last_user_message = message
        self.touch()

    def record_agent_message(self, message: str) -> None:
        """
        Update conversation state when a new agent message is produced.
        """
        self.conversation.last_agent_message = message
        self.touch()

    def apply_requirement_spec(self, spec: RequirementSpec) -> None:
        """
        Save the latest requirement specification into project state.

        This method also synchronizes missing fields and open questions with the
        spec-level agent hints, which is useful for the early MVP.
        """
        self.requirement_spec = spec
        self.missing_fields = list(spec.known_missing_fields)
        self.open_questions = list(spec.clarification_questions)

        if self.missing_fields:
            self.stage = ProjectStage.REQUIREMENT_CLARIFICATION
            self.status = ProjectStatus.WAITING_FOR_USER
        else:
            self.stage = ProjectStage.REQUIREMENT_COLLECTION
            self.status = ProjectStatus.ACTIVE

        self.touch()

    def apply_planner_decision(self, decision: PlannerDecision) -> None:
        """
        Save planner output and reflect obvious state transitions.

        This keeps the mutation logic explicit instead of scattering it across
        orchestrator/service code.
        """
        self.last_planner_decision = decision
        self.missing_fields = list(decision.missing_fields)
        self.open_questions = list(decision.clarification_questions)

        if decision.target_stage is not None:
            self.stage = decision.target_stage

        if decision.next_action == PlannerAction.ASK_USER_FOR_CLARIFICATION:
            self.status = ProjectStatus.WAITING_FOR_USER
        elif decision.next_action == PlannerAction.FAIL_PROJECT:
            self.status = ProjectStatus.FAILED
            if decision.reason:
                self.errors.append(decision.reason)
        else:
            self.status = ProjectStatus.ACTIVE

        self.touch()

    def mark_completed(self) -> None:
        """
        Mark the project as completed.
        """
        self.stage = ProjectStage.COMPLETED
        self.status = ProjectStatus.DONE
        self.touch()

    def mark_error(self, error_message: str) -> None:
        """
        Mark the project as errored and store the error message.
        """
        self.stage = ProjectStage.ERROR
        self.status = ProjectStatus.FAILED
        self.errors.append(error_message)
        self.touch()

    @property
    def has_requirements(self) -> bool:
        """
        Whether a requirement spec already exists.
        """
        return self.requirement_spec is not None

    @property
    def is_waiting_for_user(self) -> bool:
        """
        Whether the project is currently blocked on user input.
        """
        return self.status == ProjectStatus.WAITING_FOR_USER

    @classmethod
    def create_initial(
        cls,
        *,
        project_id: str,
        session_id: str,
    ) -> "ProjectState":
        """
        Create a fresh initial project state for a new session/project pair.
        """
        return cls(
            project_id=project_id,
            stage=ProjectStage.INIT,
            status=ProjectStatus.IDLE,
            conversation=ConversationState(session_id=session_id),
        )