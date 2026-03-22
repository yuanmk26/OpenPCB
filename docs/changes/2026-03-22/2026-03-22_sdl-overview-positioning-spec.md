# 2026-03-22 SDL Overview Positioning Spec Expansion

## 变更前问题
- `docs/sdl/overview.md` was a short scaffold and did not fully explain SDL positioning in OpenPCB.
- Audience-specific guidance for developers, agent/LLM engineers, and collaborators was insufficient.
- Relationship boundaries between SDL, GUI, schematic artifacts, layout artifacts, agents, and exporters were not explicit enough.

## 变更内容
- Rewrote `docs/sdl/overview.md` into a structured practical overview.
- Added required sections:
  - Introduction
  - Design Goals
  - Architectural Position in OpenPCB
  - Boundaries and Non-Goals
  - Current Version Scope (v0.1)
  - Minimal SDL Example and Walkthrough
- Added a compact Block DSL example and block-by-block explanation.
- Added explicit rationale for treating SDL as the authoritative description in the current phase.

## 影响范围
- Documentation only.
- No parser, runtime, GUI, schematic exporter, or layout exporter implementation changes.
- No changes to SDL syntax spec or semantic rule files in this update.

## 验证结果
- Confirmed the updated overview is fully in English.
- Confirmed required topic coverage is present and concretely tied to OpenPCB workflow concerns.
- Confirmed the minimal SDL example follows current Block DSL style and includes section-level explanation.

## 下一步建议
- Add cross-links from `overview.md` to specific subsections in `syntax-spec.md` and `semantic-rules.md`.
- Add one composition-oriented mini example in overview to complement the single-module example.
- Define versioning policy wording for future SDL spec stabilization milestones.
