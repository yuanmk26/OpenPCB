# SDL Authoring Guide

## Purpose
This guide provides practical authoring rules for engineers and agents writing `.opsdl` files.

## Authoring Principles
- Keep one coherent module intent per file.
- Use stable object ids to support deterministic patching.
- Prefer explicit net and port names over implicit defaults.

## Style Conventions
- Use concise and consistent naming (`U1`, `R1`, `NET_3V3`).
- Keep comments factual and close to the related block.
- Group related components and nets to improve reviewability.

## Recommended Workflow
1. Define module metadata.
2. Add components and key pins.
3. Add ports and nets.
4. Add constraints and variant notes.
5. Run validation and normalize formatting.

## Review Checklist
- Required fields present for each object type.
- No unresolved endpoints in nets.
- No contradictory constraints.
