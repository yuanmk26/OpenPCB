# OpenPCB SDL Overview

## Scope
OpenPCB SDL is a domain language for describing schematic design intent in a form that is readable by engineers and editable by agents.
The language focuses on electrical meaning, object relationships, and deterministic updates.

## Goals
- Define a clear, reviewable source format for schematic intent.
- Enable agent-based generation, modification, and validation workflows.
- Keep language semantics explicit enough to support later compilation steps.

## Non-Goals for This Draft
- No parser implementation details.
- No internal TypeScript/Python runtime model definition.
- No GUI interaction protocol.
- No direct exporter contract to specific EDA tools.

## SDL as Authority
SDL text is treated as the primary design contract in this phase.
Runtime structures can exist later, but they must map back to SDL definitions.

## Draft Maturity
This version is a scaffold for terminology, syntax, semantics, examples, and process guides.
All sections are expected to evolve with implementation feedback.
