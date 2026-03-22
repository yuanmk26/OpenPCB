# 2026-03-22 SDL Docs Skeleton Bootstrap

## 变更前问题
- The repository did not have a complete SDL documentation system.
- `docs/sdl/README.md` and `docs/sdl/overview.md` existed but were empty.
- There were no SDL example `.opsdl` files under `docs/sdl/examples/`.

## 变更内容
- Created and populated SDL draft documents under `docs/sdl/`:
  - README, overview, terminology, object dictionary, semantic rules, syntax spec.
  - examples catalog, authoring guide, schematic/layout generation guides.
  - validation guide, patch guide, roadmap, changelog.
- Added six minimal topic-oriented `.opsdl` examples in `docs/sdl/examples/`.
- Aligned example syntax with the Block DSL conventions documented in `syntax-spec.md`.

## 影响范围
- Documentation scope only; no source code, runtime behavior, parser, GUI, or exporter implementation changes.
- New SDL docs now provide a structured starting point for future language evolution.

## 验证结果
- Verified all requested files exist at the expected paths.
- Verified each Markdown file contains a title and multiple second-level sections.
- Verified examples are readable and mapped to the topics listed in `docs/sdl/examples.md`.

## 下一步建议
- Add a machine-checkable grammar profile for the draft syntax.
- Expand object dictionary with formal field types and constraints.
- Introduce validation rule IDs and error code conventions for tooling.
