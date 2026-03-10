# OpenPCB Mode-Action Architecture (Target v1)

## Purpose

This document defines the orchestration axis for PCB work:

- `mode` describes the current work perspective
- `action` describes what the agent is trying to do
- `toolchain` remains an implementation detail resolved by policy

It is intentionally independent from concrete EDA tools.

## Design rules

- Do not bind `mode` directly to a tool implementation.
- Do not model `mode` as a strict one-way pipeline state.
- Keep `action` smaller and more stable than the set of modes.
- Let policy decide toolchains, not the top-level router.

## Recommended initial modes

| Mode | Focus |
| --- | --- |
| `system_architecture` | board goals, module partitioning, interfaces, power domains |
| `schematic_design` | schematic structure, component choices, net intent |
| `schematic_check` | ERC-like review, missing connections, consistency checks |
| `placement` | floorplanning, placement constraints, thermal/mechanical concerns |
| `power_layout` | current paths, decoupling, return paths, power integrity heuristics |
| `routing` | routing priorities, critical nets, differential pairs, interference risks |

## Recommended initial actions

| Action | Meaning |
| --- | --- |
| `analyze` | understand current context and constraints |
| `plan` | produce a structured next-step design plan |
| `generate` | generate or derive structured outputs |
| `check` | validate against rules or heuristics |
| `edit` | modify an existing design representation |
| `review` | explain tradeoffs and assess quality |
| `export` | produce downstream artifacts |

## Policy resolution contract

Suggested contract:

```text
resolve(mode, action, session_state) -> ToolchainSpec
```

Where `ToolchainSpec` may contain:

- ordered abstract step ids
- allowed side effects
- prompt profile
- required inputs
- output schema

## v1 implementation constraints

- only implement `system_architecture` and `schematic_design`
- only implement `plan` and `check`
- keep all toolchain steps abstract or mapped to existing planner/checker pieces

## Current landing (2026-03)

Implementation status: `进行中`.

- `current_mode` is persisted in session and can be restored from previous session logs.
- Entry flow has a requirement gate before `plan`:
  - requirement classification (`board_class + board_family`)
  - architecture brief collection (6 required fields)
  - hard gate before `plan` execution
- Routing still uses `task_type` execution in runtime; `(mode, action) -> toolchain` policy is not implemented yet.

This means mode-awareness has started at session/conversation level, but runtime orchestration is still task-centric.

## Future extension

This structure supports later additions such as:

- mode-specific memory
- explicit mode switch commands
- mixed-mode review flows
- more specialized PCB rule engines
