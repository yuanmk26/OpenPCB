# SDL Roadmap

## Purpose
Track SDL maturation in a sequence aligned with OpenPCB architecture policy.

## Milestone M1: Authoritative SDL Baseline (Current)
- Lock SDL positioning as authoritative description.
- Align object dictionary, semantic rules, syntax, and examples.
- Establish patch-first agent operation guidance.

## Milestone M2: Layered Generation Semantics
- Stabilize schematic chain layering contracts.
- Stabilize layout chain layering contracts.
- Define minimum runtime normalized model interface for tools.

## Milestone M3: Validation and Policy Maturity
- Expand completeness checks and profile packs.
- Formalize power-domain and topology checks.
- Add stronger connector-protection policy coverage.

## Milestone M4: Tooling and Compatibility
- Integrate parser/validator/exporter implementations against SDL contracts.
- Publish compatibility and migration notes for syntax/semantic revisions.

## Risks
- Over-expanding scope into full geometry too early.
- Allowing ad-hoc direct text rewrites to bypass structured patch workflows.
- Divergence between examples and semantic rules if updates are not synchronized.
