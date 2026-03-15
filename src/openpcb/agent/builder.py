"""Mock builder that writes build artifacts to disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_artifacts(project: dict[str, Any], output_dir: Path) -> dict[str, str]:
    kicad_dir = output_dir / "kicad"
    reports_dir = output_dir / "reports"
    kicad_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    project_name = project.get("name", "project")
    kicad_pro = kicad_dir / f"{project_name}.kicad_pro"
    kicad_sch = kicad_dir / f"{project_name}.kicad_sch"
    bom_file = output_dir / "bom.json"
    netlist_file = output_dir / "netlist.json"
    report_file = reports_dir / "build-report.md"

    kicad_pro.write_text(
        f"(kicad_pro (version 20240101) (generator openpcb) (project \"{project_name}\"))\n",
        encoding="utf-8",
    )
    kicad_sch.write_text(
        f"(kicad_sch (version 20240101) (generator openpcb) (title_block (title \"{project_name}\")))\n",
        encoding="utf-8",
    )

    modules = project.get("modules", [])
    bom_payload = [
        {"ref": f"U{i+1}", "value": mod.get("name", "module"), "footprint": ""}
        for i, mod in enumerate(modules)
    ]
    netlist_payload = {
        "nets": [
            {"name": "GND", "nodes": ["U1:1"]},
            {"name": "3V3", "nodes": ["U1:2"]},
        ]
    }
    bom_file.write_text(json.dumps(bom_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    netlist_file.write_text(
        json.dumps(netlist_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report_file.write_text(
        "# Build Report\n\n"
        f"- Project: `{project_name}`\n"
        f"- Modules: `{len(modules)}`\n"
        "- Status: success\n",
        encoding="utf-8",
    )

    return {
        "kicad_pro": str(kicad_pro),
        "kicad_sch": str(kicad_sch),
        "bom": str(bom_file),
        "netlist": str(netlist_file),
        "report": str(report_file),
    }
