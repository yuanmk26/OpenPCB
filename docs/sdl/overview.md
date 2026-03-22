# OpenPCB SDL Overview

## Introduction
OpenPCB SDL (Schematic Description Language) is the textual contract used to describe schematic design intent in OpenPCB.
It is designed for three practical audiences:
- OpenPCB developers who need a stable semantic center for implementation.
- Agent and LLM engineers who need deterministic read/write and validation targets.
- Collaborators who need a clear statement of what OpenPCB design data means at this stage.

This document defines SDL positioning, boundaries, and current scope.
SDL is intentionally authored as an engineering language, not as a low-level JSON-like configuration surface.
Detailed syntax and semantics are defined in `syntax-spec.md`, `semantic-rules.md`, and `object-dictionary.md`.

## Design Goals
The current SDL draft focuses on engineering utility instead of language completeness.

Primary goals:
- Provide a reviewable, versioned, text-first source for schematic intent.
- Represent electrical objects and connectivity with explicit, machine-checkable semantics.
- Support deterministic agent workflows for generation, patching, and validation.
- Keep the language narrow enough to stabilize quickly while still useful for real project iteration.
- Keep circuit expression human-readable with interface-first, module-first, and direct-connect statements.

## Architectural Position in OpenPCB
SDL is the center contract between authoring, automation, and downstream artifacts.

### SDL and GUI
- GUI is a producer/consumer interface for design editing and inspection.
- GUI state is not the authority; SDL text remains the canonical contract.
- GUI operations should map to explicit SDL objects and changes.

### SDL and Schematic Artifacts
- Schematic visual views/files are treated as derived representations of SDL intent.
- SDL defines interfaces, module ports, instance wiring, topology, and design constraints that those views reflect.

### SDL and Layout Artifacts
- In v0.1, SDL carries schematic semantics plus selected bridge metadata for layout handoff.
- SDL is not yet a full geometry/routing/manufacturing language.
- Layout-specific completeness is intentionally deferred.

### SDL and Agent/LLM Workflows
- Agents read SDL to understand current design intent.
- Agents write SDL patches to add, modify, or remove intent in deterministic units at statement/module granularity.
- Validation uses SDL syntax and semantic rules as acceptance gates.

### SDL and Exporters
- Exporters consume normalized and resolved SDL meaning.
- Export behavior should depend on SDL semantics, not implicit GUI state.
- Exporter-specific details are out of scope for this overview.

### Why SDL as Authority Is Reasonable at This Stage
- It enables deterministic diffs and patches for human review and automated workflows.
- It gives agent systems a stable and explicit edit surface.
- It avoids coupling core design meaning to early GUI or exporter implementation choices.
- It creates a single semantic source before parser/runtime/export maturity.
- It keeps design discussions focused on electrical intent (`connect`, `topology`, `require`) instead of low-level IR encoding.

## Boundaries and Non-Goals
SDL currently solves:
- Schematic-level semantics centered on interface/module/instance composition.
- Connectivity intent and reference relationships through direct wiring statements.
- Bridge-level metadata needed to hand intent to downstream schematic/layout/export stages.

SDL does not currently solve:
- Full PCB stack definition including complete physical layout specification.
- Full routing geometry, layer-stack authoring, and manufacturing-ready CAM semantics.
- Tool-specific runtime behavior contracts for every parser/GUI/export implementation.

## Current Version Scope (v0.1)
v0.1 is a draft contract focused on schematic semantics and related bridge semantics.

Included in scope:
- Indentation-first engineering DSL syntax draft for `.opsdl`.
- Core object dictionary and baseline semantic statements.
- Semantic normalization and validation-oriented rules.
- Minimal but concrete examples for common board sub-block patterns.

Out of scope in v0.1:
- Final grammar lock and compatibility guarantees.
- Complete layout language model.
- End-to-end production toolchain contract.

## Minimal SDL Example and Walkthrough
Example:

```text
interface PowerRail:
    vin: PowerIn
    gnd: Ground
    vout: PowerOut

module LDO_Block(vout=3.3V):
    port pwr: PowerRail

    inst u_ldo: AMS1117(vout=vout) [role=regulator]
    inst c_in: C(value=10uF)
    inst c_out: C(value=22uF)

    connect pwr.vin -> [u_ldo.vin, c_in.1]
    connect pwr.vout -> [u_ldo.vout, c_out.1]
    connect pwr.gnd -> [u_ldo.gnd, c_in.2, c_out.2]

    require decoupling for u_ldo
    place [u_ldo, c_in, c_out] compact
```

Walkthrough:
- `interface PowerRail` defines a reusable external contract rather than repeated ad-hoc scalar ports.
- `module LDO_Block(vout=3.3V)` shows parameterized module authoring.
- `inst` statements identify concrete parts and module internals.
- `connect` statements make electrical intent obvious at a glance.
- `require` and `place` stay independent from wiring, so review can separate function, constraints, and physical intent.

Downstream implication:
- A GUI can map interactions back to stable design statements.
- An agent can patch intent-level lines (`connect`, `require`, `map`) without rewriting unrelated structure.
- A schematic/export stage can derive consistent connectivity from the same canonical design expression.
