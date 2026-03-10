# 2026-03-10 A1 conversation-first 默认入口验收落地

## 1. 变更前问题

- A1 在项目 TODO 中状态仍为 `未开始`，与当前 CLI 实际无参进入 REPL 的行为不一致。
- `/help` 输出只有命令清单，未明确展示 mode 信息，不满足“查看命令与模式”的验收表述。
- 缺少针对 `openpcb chat` 兼容别名行为的独立入口测试。

## 2. 变更内容

- 更新 REPL 帮助输出：在命令列表后新增 `Modes (v1)`，展示：
  - `system_architecture`
  - `schematic_design`
- 新增/增强 CLI 测试：
  - `test_root_no_args_enters_chat_repl` 增加 `/help` 输出断言，校验模式信息可见。
  - 新增 `test_chat_command_is_alias_for_repl`，校验 `openpcb chat` 仍可进入并退出 REPL。
- 更新项目任务状态：`docs/project/TODO.md` 中 A1 标记为 `已完成`，并从 P2 优先级列表移除。

## 3. 影响范围

- 修改文件：`openpcb/cli/presenter.py`
- 修改文件：`tests/cli/test_help.py`
- 修改文件：`docs/project/TODO.md`
- 新增文件：`docs/changes/2026-03-10/2026-03-10_a1-conversation-first-default-entry.md`

## 4. 验证结果

- 已通过代码检查确认：
  - `openpcb` 无参数路径进入 chat REPL（callback 默认分发）。
  - `/help` 输出中包含 `Modes (v1)` 与两个模式项。
  - `openpcb chat` 仍作为兼容别名进入 REPL。
- 尝试执行测试命令：`python -m pytest tests/cli/test_help.py tests/cli/test_chat.py`
- 结果：本地环境缺少 `pytest`（`No module named pytest`），未能完成自动化执行验证。

## 5. 下一步建议

1. 在开发环境安装测试依赖后重跑：`python -m pytest tests/cli/test_help.py tests/cli/test_chat.py`。
2. 后续推进 A2/A3 时，为 `WorkProposal` 路由与确认机制补充独立会话测试。
