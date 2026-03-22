# OpenPCB SDL Overview

## Introduction
OpenPCB SDL is a schematic-oriented design language used as the authoritative description of circuit intent.
It serves three direct audiences:
- OpenPCB developers implementing parsing, validation, and generation pipelines.
- Agent/LLM engineers integrating structured edit and review workflows.
- Collaborators who need a stable view of design semantics and project boundaries.

## Positioning in OpenPCB
SDL is the upstream semantic contract in the current architecture:
- `SDL -> parser/loader -> derived runtime structure -> validation/generation/export`.
- SDL files are authoritative and human-reviewable.
- Runtime structures are operational derivatives, not a competing source of truth.

## Problems SDL Solves
- Provides one version-controlled language for module structure, interfaces, connectivity, and engineering intent.
- Supports reusable module composition and hierarchical design.
- Supports deterministic patch-style local edits for agents.
- Supports consistent input for schematic/layout generation chains.

## What SDL Does Not Cover
- Not final schematic file geometry.
- Not final PCB geometry.
- Not GUI-internal persistence format.
- Not full simulation, full thermal, or full supply-chain optimization semantics in this phase.

## Relationships to Other System Parts
### GUI
- GUI edits and displays design state through SDL semantics.
- GUI state must map to SDL and should not become an independent authority layer.

### Schematic Artifacts
- Schematic files/views are downstream renderings from SDL-derived models.
- SDL describes semantic intent before diagram geometry.

### Layout Artifacts
- SDL provides bridge semantics for layout preparation (domains, constraints, hints).
- SDL does not directly encode final board geometry.

### Agent Workflows
- Recommended mainline: structured patch/tool operations on SDL-derived structure.
- Direct large free-form text rewrites are discouraged because they increase semantic drift risk.

### Exporters
- Exporters consume normalized SDL-derived structures.
- Exporters must follow SDL semantics, not ad-hoc assumptions from visual layout alone.

## Why SDL as Authoritative Description Is Reasonable Now
- Keeps architecture simple while implementation is still maturing.
- Preserves one human-readable and reviewable source of truth.
- Enables deterministic diffs and controlled local updates.
- Avoids premature coupling to one GUI schema or one exporter schema.

## Current Scope Boundary (v0.1)
In-scope:
- Schematic semantics.
- Module hierarchy and reuse.
- Interface modeling and mapping.
- Connectivity semantics and topology intent.
- Constraint, requirement, placement hint, and power-domain bridge semantics.

Out-of-scope:
- Full-stack PCB authoring semantics.
- Complete physical-geometry semantics.
- Full production-grade domain models for simulation/thermal/supply chain.

## Minimal Example
```text
interface PowerRail3V3:
    vdd: PowerIn
    gnd: Ground

module LDO_Block(vout=3.3V):
    port pwr_in: PowerRail3V3
    port pwr_out: PowerRail3V3

    inst u_ldo: AMS1117(vout=vout) [role=regulator]
    inst c_in: C(value=10uF)
    inst c_out: C(value=22uF)

    connect pwr_in.vdd -> [u_ldo.vin, c_in.1]
    connect pwr_out.vdd -> [u_ldo.vout, c_out.1]
    tie pwr_in.gnd = pwr_out.gnd
    connect pwr_in.gnd -> [u_ldo.gnd, c_in.2, c_out.2]

    require decoupling for u_ldo
    place [u_ldo, c_in, c_out] compact
```

## Example Notes
- `interface` captures structured external semantics.
- `module` with parameters captures reusable architecture blocks.
- `connect`/`tie` capture connectivity.
- `require`/`place` capture implementation intent separate from connectivity.
