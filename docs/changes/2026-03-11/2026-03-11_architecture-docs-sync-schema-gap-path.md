# 2026-03-11 架构文档同步：Schema 缺口驱动链路

## 背景

近期架构补全链路已收敛为“模板字段 + schema 缺口驱动 + LLM 动态问句”，但 `docs/architecture` 仍包含旧 `brief_collector` 与旧测试引用，导致文档与实现不一致。

## 本次更新

- 更新 `docs/architecture/agent-architecture.md`：
  - 将 Requirement Gate 层改为当前实现：
    - `RequirementClassifier`
    - `ArchitectureSchemaCollector`
    - `SchemaQuestionGenerator`
  - 明确当前补全流程为“单轮单题 + 1/2/3/4 选项协议”。
  - 明确 readiness 与状态输出：
    - `architecture_ready`
    - `schematic_ready`
    - `layout_ready`
    - `missing_fields`
    - `assumptions`
  - 更新测试映射到新测试文件。

- 更新 `docs/architecture/pcb-pipeline-architecture.md`：
  - 将对话衔接边界改为 schema 缺口驱动门禁。
  - 明确 `plan` 前门禁基于 `architecture_ready`。
  - 明确 metadata 注入字段：
    - `classification`
    - `architecture_brief`
    - `architecture_brief_sources`
    - `architecture_stage_status`
    - `architecture_brief_template_id`
    - `architecture_brief_template_version`
  - 更新测试映射中的旧 `test_brief_collector.py` 引用。

## 影响文件

- `docs/architecture/agent-architecture.md`
- `docs/architecture/pcb-pipeline-architecture.md`
- `docs/changes/2026-03-11/2026-03-11_architecture-docs-sync-schema-gap-path.md`

## 验证

- 通过关键字回扫确认 `docs/architecture` 中不再引用：
  - `tests/agent/test_brief_collector.py`
  - `ArchitectureBriefCollector`（旧链路语义）
- 文档现状与当前代码主链路保持一致。