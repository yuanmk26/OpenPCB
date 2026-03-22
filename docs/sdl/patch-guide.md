# SDL Patch Guide

## Purpose
This guide defines deterministic patch patterns for editing SDL documents by tools or agents.

## Patch Principles
- Target objects by stable ids or explicit paths.
- Keep patches minimal and single-intent when possible.
- Preserve non-semantic formatting where feasible.

## Patch Operations
- `add`: introduce a new object or property.
- `update`: replace or adjust an existing property value.
- `remove`: delete an object or property by exact target.
- `move` (optional): relocate block position without semantic change.

## Conflict Handling
- Detect concurrent edits on the same target path.
- Prefer explicit conflict diagnostics over silent merge.
- Require rebase/recompute when identity resolution is ambiguous.

## Validation After Patch
- Re-run syntax and semantic validation.
- Re-normalize ordering for deterministic diff output.
