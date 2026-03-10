# 2026-03-09_interactive-cli-repl

## 变更前问题

- CLI 以一次性命令调用为主，缺少交互式会话模式。
- 用户无法在同一会话内自然推进 `plan -> build -> check -> edit`。

## 变更内容

- 新增 `openpcb chat` 交互命令：
  - 文件：`openpcb/cli/commands/chat.py`
  - 支持会话命令：文本 plan、`/build`、`/check`、`/edit`、`/status`、`/help`、`/exit`
- 新增会话状态层：
  - 文件：`openpcb/agent/session.py`
  - 记录字段：`session_id/project_dir/project_json_path/last_plan/last_artifacts/history`
  - 持久化：`logs/session-*.jsonl`
- CLI 主入口注册 `chat` 命令：
  - 文件：`openpcb/cli/main.py`
- 更新任务与文档：
  - `docs/project/TODO_LIST.md` 新增 Milestone H（Interactive CLI）
  - `README.md` 新增“交互式使用（REPL）”小节

## 影响范围

- 受影响模块：
  - `openpcb/cli/main.py`
  - `openpcb/cli/commands/chat.py`
  - `openpcb/agent/session.py`
- 新增测试：
  - `tests/agent/test_session.py`
  - `tests/cli/test_chat.py`

## 验证结果

- 集成测试覆盖会话主链路与错误恢复：
  - `需求文本 -> /build -> /check -> /exit`
  - 未先 plan 时 `/build` 的提示与不中断行为

## 下一步建议

1. 后续补 `/config` 会话内动态切换模型配置能力。
2. 可增加会话摘要 markdown 以提升可读性（当前仅 JSONL）。

