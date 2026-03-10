# 2026-03-10 架构文档同步更新（分类门禁与架构补全）

## 1. 变更前问题

- 架构文档仍主要描述早期会话能力，未完整反映“需求分类 + 架构信息补全门禁”的最新实现。
- `Agent` 层文档对当前状态与目标状态混杂，且存在历史编码异常内容。
- PCB 主链路文档中“与对话系统衔接”状态落后于代码事实。

## 2. 变更内容

- 更新 `docs/architecture/agent-architecture.md`：
  - 同步当前已实现会话门禁能力（分类、补全、硬门禁、metadata 注入）。
  - 明确当前问题与下一步（ModeRouter/ActionResolver/Policy 仍未落地）。
  - 更新测试映射到新增测试集合。
- 更新 `docs/architecture/mode-action-architecture.md`：
  - 增补 `Current landing (2026-03)`，说明 mode-aware 已在会话层落地，但 runtime 仍 task-centric。
  - 清理并重写为无编码异常版本。
- 更新 `docs/architecture/pcb-pipeline-architecture.md`：
  - 将“与对话系统衔接”状态更新为 `进行中`。
  - 增加当前已落地的前置门禁边界与 metadata 输入契约。
  - 更新测试映射与下一步任务表述。

## 3. 影响范围

- 修改文件：
  - `docs/architecture/agent-architecture.md`
  - `docs/architecture/mode-action-architecture.md`
  - `docs/architecture/pcb-pipeline-architecture.md`
- 新增文件：
  - `docs/changes/2026-03-10/2026-03-10_architecture-docs-sync-classification-brief-gate.md`

## 4. 验证结果

- 已核对文档与当前实现一致：
  - `RequirementClassifier`
  - `ArchitectureBriefCollector`
  - `current_mode` 持久化与恢复
  - `project.metadata.classification/architecture_brief` 注入
- 本次仅文档更新，无运行时代码行为变更。

## 5. 下一步建议

1. 在实现 B2/B3（ModeRouter/ActionResolver/Policy）时继续保持文档与代码同日同步。
2. 将 `WorkProposal` 的标准输入结构在架构文档中进一步格式化为固定契约（字段级）。
3. 补一轮文档术语统一（中英混排与命名统一）以降低维护成本。
