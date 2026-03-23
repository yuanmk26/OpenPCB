# OpenPCB Project Knowledge Base

## Purpose

This document is the consolidated project information base for OpenPCB.
It captures stable, repository-grounded facts for planning, architecture alignment, and agent collaboration.

## Maintenance Owner

Primary maintenance role: `Project-Info Agent`.

- Responsibility: keep this document synchronized with architecture docs, SDL docs, and project-management docs.
- Constraint: prefer evidence from repository documents and code facts; do not record unsupported assumptions as confirmed facts.

## Source Priority

When updating this knowledge base, use the following source priority:

1. Current repository facts (files, directory structure, implemented modules)
2. Architecture docs under `docs/architecture/`
3. SDL docs under `docs/sdl/`
4. Project planning docs under `docs/project/`
5. Explicitly accepted decisions from user instructions

## Update Triggers

Update this file when any of the following changes:

- Architecture documents are updated (especially system/agent architecture)
- SDL positioning, rules, or generation-chain assumptions are updated
- Main workflow or agent responsibility boundaries are updated

## Project Goal

- Build OpenPCB as a design-intent-driven PCB engineering system.
- Use SDL as upstream semantic contract.
- Evolve orchestration toward `pi-mono + agent-team`.

## Current Capabilities

- Architecture and SDL documentation frameworks are present.
- Agent shell and runtime baseline exist in repository implementation.
- GUI subproject exists as a Tauri + React + TypeScript shell.

## Constraints

- Do not describe unimplemented capability as implemented.
- Keep terminology consistent with SDL docs and architecture docs.
- Worker agents do not directly own final user-visible conclusions.

## Milestones (Current Direction)

- Land `Master Agent + 3 Worker Agents` architecture definition.
- Keep SDL as semantic authority for design intent.
- Progressively close SDL-to-schematic semantic gaps.

## Risks

- Runtime delegation model is still under transition.
- SDL-to-schematic semantic completeness is not finalized.
- Inconsistent doc updates may cause knowledge drift.

## Open Decisions

- Worker execution lifecycle schema and retry policy detail
- SDL-to-schematic semantic contract granularity
- Runtime observability depth for multi-agent orchestration

## Update Checklist

Use this checklist for each update:

1. Confirm changed facts from repository/docs.
2. Update affected sections in this file.
3. Cross-check terms against `docs/architecture/` and `docs/sdl/`.
4. Add a same-day record under `docs/changes/<YYYY-MM-DD>/`.
