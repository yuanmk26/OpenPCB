# 2026-03-10 Claude 式对话体验改造

## 变更前问题
- `openpcb chat` 主要是命令驱动（`/build`、`/check`、`/edit`），普通文本只会走 `plan`。
- 写盘动作没有统一确认机制，误触发风险较高。
- 运行时异常（例如缺 API key）可能直接抛出 traceback，REPL 中断。
- 会话日志缺少“决策与确认”字段，无法回放“为什么执行这个动作”。

## 变更内容
- 新增对话编排层：`openpcb/agent/conversation.py`
  - 增加 `ConversationDecision` 数据结构。
  - 增加 `decide_action(...)`，基于关键词将普通文本路由到 `plan/build/check/edit` 或澄清分支。
- 扩展会话状态：`openpcb/agent/session.py`
  - 新增 `PendingAction`。
  - `ChatSession` 新增 `pending_action`、`last_user_goal`、`last_decision`、`last_result_summary`。
- 新增统一展示层：`openpcb/cli/presenter.py`
  - 统一输出“结论 + 关键变化 + trace 路径”的回复结构。
  - 统一帮助信息、状态信息、确认提示。
- 重构 `openpcb/cli/commands/chat.py`
  - 默认文本改为“自动决策路由”。
  - 增加 `/yes`、`/no` 确认流。
  - `build/edit` 在执行前要求确认。
  - 对 `OpenPCBError` 和未知异常做兜底，不退出 REPL。
  - 增强会话日志字段：`decision/requires_confirmation/confirmed/action_route/reply_style`。
- 测试更新
  - 更新 `tests/cli/test_chat.py`，覆盖确认流与新输出。
  - 新增 `tests/agent/test_conversation.py`，覆盖文本到动作路由逻辑。
- 文档更新
  - `README.md` 新增 `Chat Mode (Conversation-Oriented)` 小节。
  - `TODO_LIST.md` 将 Milestone H（H1~H5）状态更新为 `已完成`。

## 影响范围
- 主要影响：`openpcb chat` 交互体验与行为语义。
- 不影响：`openpcb plan/build/check/edit` 非交互命令接口。
- 新增文件：
  - `openpcb/agent/conversation.py`
  - `openpcb/cli/presenter.py`
  - `tests/agent/test_conversation.py`

## 验证结果
- 已补充/更新自动化测试：
  - `tests/cli/test_chat.py`
  - `tests/agent/test_conversation.py`
- 验证目标：
  - 普通文本可自动路由。
  - `build/edit` 先确认后执行。
  - 无项目时触发 `build` 会给出明确提示。
  - 会话日志可记录决策与确认字段。

## 下一步建议
1. 将当前关键词路由升级为“LLM 决策 + 规则兜底”双通道。
2. 增加 `/undo` 或“最近一步回滚”能力，降低编辑试错成本。
3. 在会话中加入 `diff` 预览（执行 `/yes` 前显示计划变更摘要）。
