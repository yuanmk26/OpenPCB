"""Project planner based on parsed intent."""

from __future__ import annotations

from openpcb.agent.parser import Intent
from openpcb.schema.enums import ModuleType
from openpcb.schema.module import ModuleSpec
from openpcb.schema.project import ProjectSpec


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
