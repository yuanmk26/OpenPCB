# SDL Authoring Guide

## Purpose
This guide provides practical authoring rules for engineers and agents writing `.opsdl` files.

## Authoring Principles
- Keep one coherent module intent per file.
- Keep SDL as design expression DSL, not as a serialized internal config format.
- Prefer interface-first boundaries and direct connectivity statements.
- Use stable instance names and explicit intent statements to support deterministic patching.

## Style Conventions
- Use indentation-based statement style.
- Do not use `module "name" {}` and heavy `key "value"` surfaces as primary authoring style.
- Keep connectivity obvious with `connect`, `tie`, and `topology`.
- Separate wiring intent from requirement and placement intent (`require`, `constrain`, `place`).
- Prefer meaningful names for modules/interfaces/instances over library-detail-heavy snippets.

## Recommended Workflow
1. Define interfaces and module signature (including parameters if needed).
2. Declare ports and instantiate parts/submodules with `inst`.
3. Express connectivity with `connect`; add explicit `net` names only where identity matters.
4. Add `map`/`expose` for composition boundaries and interface binding.
5. Add `topology`, `constrain`, `require`, `place`, and `domain` intent statements.
6. Run validation and normalize ordering for deterministic diffs.

## Review Checklist
- Interfaces and ports communicate module boundaries clearly.
- `connect` lines make electrical relationships immediately understandable.
- `topology` statements are used where path order is important.
- `constrain` and `require` are not mixed semantically.
- Placement and requirement intent are explicit and reviewable.
