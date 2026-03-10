# 2026-03-10 B1 Session current_mode 持久化与恢复

## 1. 变更前问题

- `ChatSession` 未保存当前工作模式，缺少 `current_mode` 状态字段。
- 会话日志无法明确追踪模式切换，难以支撑 mode-action 架构演进。
- 重新进入同一项目会话时不能恢复上一轮模式视角，用户上下文会丢失。

## 2. 变更内容

- 在 `ChatSession` 中新增 `current_mode` 字段，默认值为 `system_architecture`。
- 新增 `set_mode(mode, source=...)` 方法：
  - 仅在模式变化时更新。
  - 记录 `mode_changed` 事件（含 `from_mode/to_mode/current_mode/source`）。
- 增加会话重入恢复机制：
  - `ChatSession.create()` 启动时扫描 `logs/session-*.jsonl`。
  - 从最近有效日志恢复最后模式。
  - 恢复成功记录 `mode_restored`，首次初始化记录 `mode_initialized`。
- 在 chat 任务执行入口按任务类型更新模式：
  - `plan -> system_architecture`
  - `build/check/edit -> schematic_design`
- 状态输出补充 `current_mode`。

## 3. 影响范围

- 修改文件：`openpcb/agent/session.py`
- 修改文件：`openpcb/cli/commands/chat.py`
- 修改文件：`openpcb/cli/presenter.py`
- 修改文件：`tests/agent/test_session.py`
- 修改文件：`docs/project/TODO.md`（B1 状态改为已完成）
- 新增文件：`docs/changes/2026-03-10/2026-03-10_b1-session-current-mode-persistence.md`

## 4. 验证结果

- 已新增并覆盖以下测试场景：
  - 模式变更事件记录：`test_session_mode_change_is_logged`
  - 会话重入模式恢复：`test_session_reentry_restores_current_mode`
- 尝试执行：`python -m pytest tests/agent/test_session.py tests/cli/test_chat.py`
- 结果：当前环境缺少 `pytest`（`No module named pytest`），未完成本地自动化执行。

## 5. 下一步建议

1. 安装测试依赖后重跑新增用例，确认 CI 与本地结果一致。
2. 在 B2 中将模式枚举收敛为统一类型（避免字符串常量分散）。
3. 在 B3 中将 `mode -> action -> toolchain` 解析链接入 runtime 主流程。
