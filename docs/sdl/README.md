# OpenPCB SDL Documentation (Draft v0.1)

## Purpose
This directory defines the SDL contract for the current OpenPCB phase.
SDL is the authoritative design description. Runtime structured models are derived from SDL for parsing, validation, generation, and patch application.

## What SDL Is
- A text language for circuit design semantics.
- A shared layer for humans, agents, review, reuse, import/export, and version control.
- The upstream contract for schematic generation, layout generation, validation, and controlled patching.

## What SDL Is Not
- Not the final schematic file format.
- Not the final PCB layout file format.
- Not the GUI storage format.
- Not a low-level geometry language.

## Documentation Map
- `overview.md`: SDL positioning, boundaries, and phase scope in OpenPCB.
- `terminology.md`: canonical terms used across SDL docs.
- `object-dictionary.md`: authoritative object system and layer model.
- `semantic-rules.md`: normative semantic rules and completeness checks.
- `syntax-spec.md`: canonical engineering DSL surface syntax.
- `examples.md`: capability matrix for `.opsdl` examples.
- `authoring-guide.md`: practical authoring and review discipline.
- `validation-guide.md`: layered validation strategy and minimum checks.
- `patch-guide.md`: structured patch workflow and operation patterns.
- `schematic-generation.md`: SDL to schematic layered generation chain.
- `layout-generation.md`: SDL to layout layered generation chain.
- `roadmap.md`: SDL maturation milestones.
- `changelog.md`: SDL documentation update history.
- `examples/`: reference SDL examples aligned to current architecture consensus.

## Recommended Reading Order
1. `overview.md`
2. `terminology.md`
3. `object-dictionary.md`
4. `semantic-rules.md`
5. `syntax-spec.md`
6. `examples.md`
7. `authoring-guide.md`
8. `validation-guide.md`
9. `patch-guide.md`
10. `schematic-generation.md`
11. `layout-generation.md`
12. `roadmap.md`
13. `changelog.md`

## Current Phase Policy
- Focus on schematic semantics and schematic/layout bridge semantics.
- Prefer module-first and interface-first modeling.
- Prefer structured patch/tool operations for agent edits over free-form large text rewrites.
- Avoid over-expanding into full simulation, full thermal, full BOM optimization, or full PCB geometry semantics in v0.1 docs.
