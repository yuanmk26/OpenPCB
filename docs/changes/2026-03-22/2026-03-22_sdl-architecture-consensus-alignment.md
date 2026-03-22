# 2026-03-22 SDL Architecture Consensus Alignment

## 变更前问题
- Existing SDL docs and examples were partially aligned but not fully consistent with the architecture consensus.
- Object taxonomy, semantic rules, generation layering, and patch positioning were not fully codified with required boundaries.
- Some documents lacked explicit separation between connectivity semantics and constraint/requirement semantics.

## 变更内容
- Rewrote `docs/sdl/` document set to align with the agreed architecture:
  - SDL authoritative description policy with derived runtime model policy.
  - module-first/interface-first design principles.
  - four-layer object system in `object-dictionary.md`.
  - full semantic rules in `semantic-rules.md`.
  - canonical syntax contract in `syntax-spec.md`.
  - capability-driven example catalog and updated `.opsdl` examples.
  - rewritten schematic/layout generation chains with explicit layered models.
  - rewritten structured patch workflow with required operation examples.
- Updated roadmap and changelog for architecture-aligned progression.

## 影响范围
- Documentation and examples only.
- No parser/runtime/GUI/exporter/source-code behavior changes.
- SDL contract clarity for future tooling integration is improved.

## 验证结果
- Verified all major files under `docs/sdl/` were updated in the requested order and with required topics.
- Verified example set now reflects module nesting, interfaces, mapping, domains, groups, topology, requirements, and placement hints.
- Verified patch guide includes all requested patch operation examples.

## 下一步建议
- Add a formal SDL lint profile for naming/ordering and anti-pattern checks.
- Add compatibility notes for future syntax evolution from v0.1 to v0.2.
- Add machine-checkable rule IDs for semantic/completeness checks.
