# OpenPCB SDL Documentation (Draft v0.1)

## Purpose
This directory defines the first draft of the OpenPCB Schematic Description Language (SDL).
At this stage, SDL documentation is the source of truth for language intent and authoring behavior.

## Document Index
- `overview.md`: scope, goals, and non-goals of SDL.
- `terminology.md`: canonical terms used across SDL docs.
- `object-dictionary.md`: SDL object catalog and required fields.
- `semantic-rules.md`: meaning and normalization rules.
- `syntax-spec.md`: lexical and structural syntax draft.
- `examples.md`: example catalog and usage notes.
- `authoring-guide.md`: writing practices for SDL files.
- `schematic-generation.md`: SDL to schematic interpretation model.
- `layout-generation.md`: SDL to layout intent handoff model.
- `validation-guide.md`: validation layers and expected checks.
- `patch-guide.md`: deterministic patch workflows for agents.
- `roadmap.md`: planned milestones for SDL evolution.
- `changelog.md`: SDL documentation change history.
- `examples/`: minimal `.opsdl` sample files.

## Recommended Reading Order
1. `overview.md`
2. `terminology.md`
3. `object-dictionary.md`
4. `syntax-spec.md`
5. `semantic-rules.md`
6. `authoring-guide.md`
7. `validation-guide.md`
8. `patch-guide.md`
9. `schematic-generation.md`
10. `layout-generation.md`
11. `examples.md`
12. `roadmap.md`
13. `changelog.md`

## Status and Boundaries
- This is a skeleton draft, not a stable spec release.
- Parser, TypeScript IR, GUI, and exporter behavior are not implemented or guaranteed here.
- Examples are intentionally compact and may omit production-level detail.
