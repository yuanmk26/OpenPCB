from __future__ import annotations

from dataclasses import dataclass

from openpcb.agent.orchestrator import Orchestrator
from openpcb.config.settings import Settings, get_settings
from openpcb.infra.llm.client import LLMClient
from openpcb.infra.llm.structured_output import StructuredOutputParser
from openpcb.planner.planner import Planner
from openpcb.services.requirement_service import RequirementService


@dataclass(slots=True)
class Application:
    """
    The top-level application container.

    This object groups together the main runtime dependencies that are
    needed by the CLI or other entrypoints.
    """

    settings: Settings
    llm_client: LLMClient
    structured_output_parser: StructuredOutputParser
    requirement_service: RequirementService
    planner: Planner
    orchestrator: Orchestrator


def build_application() -> Application:
    """
    Build and wire the minimum OpenPCB application.

    Dependency graph (minimal version):

        Settings
           │
           └──> LLMClient
                    │
                    └──> RequirementService
        StructuredOutputParser ───────┘

        Planner
           │
           └──────────────────────────> Orchestrator
                         RequirementService ───────┘

    Returns:
        Application: a fully wired application object.
    """
    settings = get_settings()

    llm_client = LLMClient(settings=settings)
    structured_output_parser = StructuredOutputParser()

    requirement_service = RequirementService(
        llm_client=llm_client,
        output_parser=structured_output_parser,
    )

    planner = Planner()

    orchestrator = Orchestrator(
        planner=planner,
        requirement_service=requirement_service,
    )

    return Application(
        settings=settings,
        llm_client=llm_client,
        structured_output_parser=structured_output_parser,
        requirement_service=requirement_service,
        planner=planner,
        orchestrator=orchestrator,
    )