"""Project planner with LLM-default and mock fallback mode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openpcb.agent.llm.factory import get_llm_client
from openpcb.agent.llm.types import LLMRequest
from openpcb.agent.parser import Intent
from openpcb.config.settings import AgentSettings
from openpcb.schema.enums import ModuleType
from openpcb.schema.module import ModuleSpec
from openpcb.schema.project import ProjectSpec
from openpcb.utils.errors import InputError


def _module_type(module_id: str) -> ModuleType:
    if module_id.startswith("mcu"):
        return ModuleType.MCU
    if module_id.startswith("power"):
        return ModuleType.POWER
    if module_id.startswith("interface"):
        return ModuleType.INTERFACE
    return ModuleType.MISC


def build_project_spec(intent: Intent, project_name: str) -> ProjectSpec:
    modules = [
        ModuleSpec(
            id=f"m{i+1}",
            type=_module_type(module_name),
            name=module_name,
            description=f"Auto planned module: {module_name}",
        )
        for i, module_name in enumerate(intent.modules or [])
    ]
    return ProjectSpec(
        name=project_name,
        description=f"Auto-generated plan for {project_name}",
        requirements=intent.requirement,
        modules=modules,
        metadata={"planner": "rule-mock-v1"},
    )


def _prompt_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / "prompts" / filename


def _read_prompt(filename: str) -> str:
    path = _prompt_path(filename)
    if not path.exists():
        raise InputError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_json_payload(text: str) -> str:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3:
            candidate = "\n".join(lines[1:-1]).strip()
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start < 0 or end < 0 or end <= start:
        raise InputError("LLM response does not contain a JSON object.")
    return candidate[start : end + 1]


def parse_project_spec_from_json(payload: str, project_name: str) -> ProjectSpec:
    try:
        data: dict[str, Any] = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise InputError("Planner JSON parsing failed.") from exc
    if "name" not in data:
        data["name"] = project_name
    if "requirements" not in data:
        data["requirements"] = ""
    if "modules" not in data:
        data["modules"] = []
    return ProjectSpec.model_validate(data)


def build_project_spec_with_llm(
    requirement: str,
    project_name: str,
    settings: AgentSettings,
) -> tuple[ProjectSpec, dict[str, Any]]:
    client = get_llm_client(settings.provider)
    system_prompt = _read_prompt("plan_system.txt")
    user_template = _read_prompt("plan_user_template.txt")
    user_prompt = user_template.format(project_name=project_name, requirement=requirement)

    llm_response = client.complete(
        LLMRequest(
            provider=settings.provider,
            model=settings.model,
            api_key=settings.api_key or "",
            base_url=settings.base_url,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
        )
    )
    json_payload = extract_json_payload(llm_response.content)
    project = parse_project_spec_from_json(json_payload, project_name=project_name)
    project.metadata["planner"] = "llm-openai-v1"
    return project, {
        "provider": llm_response.provider,
        "model": llm_response.model,
        "token_usage": llm_response.token_usage,
        "latency_ms": llm_response.latency_ms,
    }
