# 2026-03-22 SDL Surface Style Migration to Engineering DSL

## 变更前问题
- SDL syntax and examples were mainly written in block-config style (`module "x" { ... }`), which looked like HCL/JSON-like configuration.
- The style did not reflect the intended engineering DSL direction (module/interface-first and direct connection expression).
- Style guidance across overview, object dictionary, and authoring guide was not fully aligned with the target SDL positioning.

## 变更内容
- Rewrote `docs/sdl/syntax-spec.md` to define indentation-first engineering DSL as the canonical surface style.
- Added explicit syntax sections and examples for `module`, `interface`, `inst`, `port`, `net`, `connect`, `expose`, `tie`, `topology`, `constrain`, `require`, `place`, `domain`, and `map`.
- Rewrote `docs/sdl/examples.md` and all example `.opsdl` files to the new DSL style.
- Updated style-positioning text in `docs/sdl/overview.md`, `docs/sdl/object-dictionary.md`, and `docs/sdl/authoring-guide.md` to emphasize SDL as design-expression DSL rather than low-level config/IR surface.

## 影响范围
- Documentation and example files only.
- No parser, runtime, GUI, exporter, or other source-code behavior changes.
- Existing SDL docs now present a consistent language surface direction for future implementation.

## 验证结果
- Verified all target docs and examples were updated to indentation engineering DSL style.
- Verified syntax spec includes all required statement categories from the migration plan.
- Verified examples demonstrate parameterized module, interface-first composition, direct connect readability, independent requirement/place/topology expressions, and nested top-level module composition.

## 下一步建议
- Add a compact "style anti-patterns" section in `syntax-spec.md` with side-by-side before/after examples.
- Define a minimal lint profile for statement ordering and naming conventions.
- Expand semantic rules to describe evaluation semantics for `map`, `tie`, and `topology` in more detail.
