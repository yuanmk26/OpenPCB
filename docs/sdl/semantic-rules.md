# SDL Semantic Rules

## Purpose
This document defines meaning-level rules beyond surface syntax.
A file can be syntactically valid and still fail semantic validation.

## Connectivity Semantics
- Every endpoint in `net.connect` must resolve to an existing pin or port.
- A single pin can appear on multiple nets only if explicitly allowed by pin type.
- Power nets should use explicit names and avoid anonymous auto-merge behavior.

## Reference Resolution
- `id` values must be unique in module scope.
- `ref` values should be unique among components in module scope.
- Cross-module references must be explicit through instance/port boundaries.

## Value and Unit Semantics
- Numeric values should include units where ambiguous (for example `10k`, `100nF`).
- Unit normalization should map equivalent forms to a canonical value representation.
- Missing units are warnings unless the object type mandates strict units.

## Deterministic Normalization
- Object lists should be normalized by stable identity (`id` then `name`).
- Equivalent net endpoint orderings should normalize to a deterministic sequence.
- Comments and formatting are non-semantic.

## Rule Severity
- `error`: blocks downstream generation or merge.
- `warning`: accepted with diagnostics for review.

## Open Items
- Final pin electrical type matrix.
- Variant merge precedence for conflicting edits.
