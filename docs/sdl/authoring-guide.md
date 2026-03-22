# SDL Authoring Guide

## Purpose
This guide defines how to author SDL files for OpenPCB v0.1 in a way that is readable, reviewable, and patch-friendly.

## Core Authoring Principles
- Module-first: model reusable blocks first, then compose.
- Interface-first: define boundary contracts before wiring internals.
- Connectivity-intent separation: keep `connect/expose/tie/topology` separate from `constrain/require/place`.
- Boundary-safe hierarchy: parent modules connect via child ports/expose, not child-private nets.
- Agent-friendly structure: stable names and paths for local patch operations.

## Recommended Authoring Flow
1. Define interfaces.
2. Define module signature and parameters.
3. Declare ports.
4. Instantiate components/modules.
5. Add connect/net/tie/topology/map statements.
6. Add constraint/require/place/domain/group intent.
7. Run validation and normalize output.

## Naming and Stability Conventions
- Use stable and explicit instance names (`u_mcu`, `pwr0`, `dbg0`).
- Keep interface member names semantic (`scl`, `sda`, `nreset`, `vtref`).
- Use deterministic group/domain names (`bringup_core`, `board_power`).
- Prefer RefPath-stable identifiers to reduce patch ambiguity.

## Authoring Anti-Patterns
- Writing SDL as generic key-value config.
- Mixing requirement obligations directly into raw connectivity lines.
- Directly reaching into child-local internal nets from parent modules.
- Large broad rewrites when local patch-style edits are possible.

## Review Checklist
- Module boundaries are explicit and respected.
- Interfaces are complete and mapping is explicit where names differ.
- Requirements are stated and checkable.
- Placement hints are intent-level and not pseudo-geometry.
- Domain definitions include source/return/provider/consumers where relevant.
