# OpenPCB Mode-Action Architecture (Target v1)

## Purpose

This document defines the new orchestration axis for PCB work:

- `mode` describes the current work perspective
- `action` describes what the agent is trying to do
- `toolchain` remains an implementation detail resolved later

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

## Session transition examples

### Example 1

`system_architecture -> plan`

The user describes a new board idea.
The agent should stay at architecture level and produce module partitioning or constraints, not jump into layout details.

### Example 2

`schematic_design -> check`

The user asks whether the current USB and power connections are complete.
The agent stays in schematic context and performs consistency-oriented checks.

### Example 3

`placement -> edit`

The user asks to move the DC-DC section away from the RF front end.
The mode stays `placement`, but the action becomes `edit`.

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

## Future extension

This structure supports later additions such as:

- mode-specific memory
- explicit mode switch commands
- mixed-mode review flows
- more specialized PCB rule engines
