# 2026-03-08_agent-runtime-and-todo-migration

## 变更前问题

- `plan/generate/check/edit` 多数还是占位命令，尚未形成可执行 Agent 链路。
- 任务主文档仍是 `openpcb_task_breakdown.md`，不适合持续 TODO 管理。
- 缺少 `build` 命令与 `generate` 兼容迁移机制。

## 变更内容

- 新增单 Agent runtime（`observe -> plan -> act -> reflect -> finalize`）：
  - 新增 `openpcb/agent/runtime.py`、`models.py`、`tooling.py`。
  - 引入 step budget、重试、trace 日志（`logs/agent-run-*.jsonl`）。
- 补齐 agent 能力模块：
  - `parser.py`：需求关键词提取。
  - `planner.py`：规则式 `ProjectSpec` 生成。
  - `builder.py`：落盘 kicad/bom/netlist/build-report。
  - `checker.py`：基础检查报告。
  - `executor.py`：规则式 edit 修改。
- 命令层重构：
  - `plan` 改为可落盘（`project.json` + `plan.md`）。
  - 新增 `build` 命令。
  - `generate` 改为 `build` 兼容别名并提示 deprecated。
  - `check/edit` 接入 runtime。
- 数据层补齐：
  - 新增 `openpcb/schema/*`（ProjectSpec/ModuleSpec/ComponentSpec/NetSpec/Enums）。
- 任务文档迁移：
  - 新增主文档 `docs/project/TODO_LIST.md`（Agent-first 里程碑结构）。
  - 原 `openpcb_task_breakdown.md` 改为迁移入口与说明。

## 影响范围

- 主要影响命令：
  - `openpcb plan`
  - `openpcb build`
  - `openpcb generate`（兼容层）
  - `openpcb check`
  - `openpcb edit`
- 主要新增文件：
  - `openpcb/agent/runtime.py`
  - `openpcb/cli/commands/build.py`
  - `docs/project/TODO_LIST.md`

## 验证结果

- 已新增/更新 CLI 测试：
  - `tests/cli/test_help.py`
  - `tests/cli/test_plan_build.py`
- 验证目标：
  - `plan` 产出 `project.json + plan.md`
  - `build` 产出 `output/kicad/* + bom.json + netlist.json + report`
  - `generate` 作为兼容别名可调用 build

## 下一步建议

1. 为 `check/edit` 增加独立 CLI 测试与错误路径测试。
2. 将 build 从 mock 输出升级为真实模板与 KiCad writer 流程。
