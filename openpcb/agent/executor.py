"""Edit executor for ProjectSpec mutations."""

from __future__ import annotations

from dataclasses import dataclass

from openpcb.schema.enums import ModuleType
from openpcb.schema.module import ModuleSpec
from openpcb.schema.project import ProjectSpec


@dataclass
class EditResult:
    project: ProjectSpec
    report: str


def apply_edit(project: ProjectSpec, instruction: str) -> EditResult:
    updated = project.model_copy(deep=True)
    lowered = instruction.lower()
    changes: list[str] = []

    if "led" in lowered:
        next_id = f"m{len(updated.modules) + 1}"
        updated.modules.append(
            ModuleSpec(
                id=next_id,
                type=ModuleType.MISC,
                name="misc_status_led",
                description="Added by edit instruction",
            )
        )
        changes.append("Added module: misc_status_led")

    if "uart" in lowered and not any(m.name == "interface_uart_header" for m in updated.modules):
        next_id = f"m{len(updated.modules) + 1}"
        updated.modules.append(
            ModuleSpec(
                id=next_id,
                type=ModuleType.INTERFACE,
                name="interface_uart_header",
                description="Added by edit instruction",
            )
        )
        changes.append("Added module: interface_uart_header")

    if not changes:
        changes.append("No rule matched; project unchanged.")

    report = "# Edit Report\n\n" + "\n".join(f"- {item}" for item in changes) + "\n"
    return EditResult(project=updated, report=report)
