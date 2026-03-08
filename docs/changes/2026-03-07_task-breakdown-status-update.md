# 2026-03-07_task-breakdown-status-update

## 变更前问题

- `openpcb_task_breakdown.md` 主要是规划态内容，缺少“当前真实进度”标识。
- 任务执行时容易把“占位实现”误判为“已完成”，影响后续排期判断。
- 文件级任务清单中 `loader/saver` 命名与当前实现不一致，容易造成定位混淆。

## 变更内容

- 在 `openpcb_task_breakdown.md` 开头新增“状态说明”小节，定义三类状态：
  - `已完成`
  - `进行中`
  - `未开始`
- 为 Milestone 0~8 的每个 `M*-T*` 任务条目补充 `状态` 行。
- 更新 Done Definition 勾选状态：
  - 已勾选 `openpcb init` 可创建项目
  - 其余 `plan/generate/check/edit/demo/README/关键路径覆盖` 保持未完成
- 在“文件级任务清单”补充每一项 `当前状态`，并新增命名偏差说明：
  - 原计划 `openpcb/io/loader.py`、`openpcb/io/saver.py`
  - 当前实现 `openpcb/io/project_loader.py`、`openpcb/io/project_saver.py`

## 影响范围

- 受影响文件：
  - `openpcb_task_breakdown.md`
- 新增文档：
  - `docs/changes/2026-03-07_task-breakdown-status-update.md`
- 本次仅为文档状态化更新，不涉及代码逻辑修改。

## 验证结果

- 结构验证：
  - 每个里程碑任务条目已加入状态行。
  - 文件级任务条目已加入当前状态行。
- 内容验证：
  - 状态值仅使用 `已完成/进行中/未开始`。
  - Done Definition 与当前实现进度一致（`help/version/init` 最小链路可用）。

## 下一步建议

1. 按当前状态化任务表进入 M3（优先实现 `plan` 的 mock 逻辑与落盘）。
2. 后续每次任务完成后继续在 `docs/changes/` 追加一份同结构解释文档，保持可追溯。

