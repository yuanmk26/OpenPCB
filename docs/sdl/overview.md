# OpenPCB SDL Overview

## Introduction
OpenPCB SDL (Schematic Description Language) is the textual contract used to describe schematic design intent in OpenPCB.
It is designed for three practical audiences:
- OpenPCB developers who need a stable semantic center for implementation.
- Agent and LLM engineers who need deterministic read/write and validation targets.
- Collaborators who need a clear statement of what OpenPCB design data means at this stage.

This document defines SDL positioning, boundaries, and current scope.
Detailed syntax and semantics are defined in the surrounding SDL document set, especially `syntax-spec.md`, `semantic-rules.md`, and `object-dictionary.md`.

## Design Goals
The current SDL draft focuses on engineering utility instead of language completeness.

Primary goals:
- Provide a reviewable, versioned, text-first source for schematic intent.
- Represent electrical objects and connectivity with explicit, machine-checkable semantics.
- Support deterministic agent workflows for generation, patching, and validation.
- Keep the language narrow enough to stabilize quickly while still useful for real project iteration.

## Architectural Position in OpenPCB
SDL is the center contract between authoring, automation, and downstream artifacts.

### SDL and GUI
- GUI is a producer/consumer interface for design editing and inspection.
- GUI state is not the authority; SDL text remains the canonical contract.
- GUI operations should map to explicit SDL objects and changes.

### SDL and Schematic Artifacts
- Schematic visual views/files are treated as derived representations of SDL intent.
- SDL defines component identity, ports, nets, and semantic constraints that those views reflect.

### SDL and Layout Artifacts
- In v0.1, SDL carries schematic semantics plus selected bridge metadata for layout handoff.
- SDL is not yet a full geometry/routing/manufacturing language.
- Layout-specific completeness is intentionally deferred.

### SDL and Agent/LLM Workflows
- Agents read SDL to understand current design intent.
- Agents write SDL patches to add, modify, or remove intent in deterministic units.
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

## Boundaries and Non-Goals
SDL currently solves:
- Schematic-level object semantics (module, component, pin, port, net, constraints).
- Connectivity intent and reference relationships.
- Bridge-level metadata needed to hand intent to downstream schematic/layout/export stages.

SDL does not currently solve:
- Full PCB stack definition including complete physical layout specification.
- Full routing geometry, layer-stack authoring, and manufacturing-ready CAM semantics.
- Tool-specific runtime behavior contracts for every parser/GUI/export implementation.

## Current Version Scope (v0.1)
v0.1 is a draft contract focused on schematic semantics and related bridge semantics.

Included in scope:
- Block DSL syntax draft for `.opsdl`.
- Core object dictionary and baseline required fields.
- Semantic normalization and validation-oriented rules.
- Minimal but concrete examples for common board sub-block patterns.

Out of scope in v0.1:
- Final grammar lock and compatibility guarantees.
- Complete layout language model.
- End-to-end production toolchain contract.

## Minimal SDL Example and Walkthrough
Example:

```text
module "power_input_min" {
  version "0.1"

  component "u_ldo1" {
    ref "U1"
    type "ldo_regulator"
    pin "IN" {}
    pin "OUT" {}
    pin "GND" {}
  }

  port "VIN" { dir "in" }
  port "VOUT_3V3" { dir "out" }

  net "VIN" { connect ["port:VIN", "U1.IN"] }
  net "VOUT_3V3" { connect ["U1.OUT", "port:VOUT_3V3"] }
}
```

Walkthrough:
- `module` and `version` define the top-level design unit and document revision context.
- `component "u_ldo1"` introduces a stable object identity with implementation-facing reference (`ref "U1"`) and logical type.
- `pin` entries expose connection points that nets can target explicitly.
- `port` entries define module external interfaces and make submodule composition possible.
- `net` blocks encode electrical connectivity by referencing endpoints (`port:*` and `U1.*`), which downstream systems can resolve deterministically.

Downstream implication:
- A GUI can present and edit these objects.
- An agent can patch one block without rewriting the full file.
- A schematic/export stage can derive consistent connectivity from the same canonical text.
