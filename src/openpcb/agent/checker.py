"""Simple rule checker for project payload."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def run_checks(project: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    reports_dir = output_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "check-report.md"

    warnings: list[str] = []
    errors: list[str] = []
    modules = project.get("modules", [])
    names = {module.get("name", "") for module in modules}

    if not modules:
        errors.append("Project has no modules.")
    if not any("power" in name for name in names):
        warnings.append("No explicit power module found.")
    if not any("mcu" in name for name in names):
        warnings.append("No MCU module found.")

    report_path.write_text(
        "# Check Report\n\n"
        f"- Errors: {len(errors)}\n"
        f"- Warnings: {len(warnings)}\n\n"
        "## Details\n\n"
        + ("\n".join(f"- ERROR: {msg}" for msg in errors) + "\n" if errors else "- No errors\n")
        + ("\n".join(f"- WARN: {msg}" for msg in warnings) + "\n" if warnings else "- No warnings\n"),
        encoding="utf-8",
    )

    return {
        "errors": errors,
        "warnings": warnings,
        "report": str(report_path),
    }
