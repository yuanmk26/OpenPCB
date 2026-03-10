# 2026-03-10 conversation-first shell 架构细化

## 变更前问题
- 当前架构文档已经覆盖了 Agent、IR 和 PCB 主链路，但缺少“默认进入交互 shell、先做纯对话”的设计细化。
- `chat` 的现状更像任务路由器，不足以支撑你想要的 Claude/Codex 风格体验。
- 文档里没有明确说明 Chat Agent、TaskRouter、Runtime 和 PCB 流水线之间的边界。

## 变更内容
- 重写 `docs/architecture/agent-architecture.md`
  - 新增 conversation-first shell 目标形态
  - 增加 `ChatAgent` v1 的职责、边界和行为约束
  - 明确 `openpcb` 默认入口从 help 转向 shell 的目标
- 重写 `docs/architecture/system-architecture.md`
  - 加入 `openpcb` 默认入口、纯聊天优先、再进入任务执行的系统流程
  - 增加 `Conversation Shell v1` 小节
  - 明确聊天历史属于中间产物的一部分
- 更新 `docs/architecture/pcb-pipeline-architecture.md`
  - 增加“与对话系统的衔接”小节
  - 明确只有确认后的 `TaskProposal` 才进入 PCB 流水线

## 影响范围
- 仅文档变更，不修改 CLI、runtime、LLM client 或 PCB builder 的现有实现。
- 这次文档把“先对话、后任务”的架构路线固定下来，便于后续按阶段落地。

## 验证结果
- 架构文档已覆盖以下关键点：
  - `openpcb` 默认进入交互 shell
  - Chat Agent v1 先做纯 LLM 对话
  - TaskRouter 负责把聊天升级为任务请求
  - PCB 流水线只接收结构化任务输入，不直接消费聊天日志

## 下一步建议
1. 先落地 `ChatSession` 的标准消息结构和 `ChatAgent`。
2. 让 `openpcb` 无参数进入 shell，并保留 `--help` 明确显示用法。
3. 纯聊天稳定后，再把 `TaskRouter` 和确认流接回 `plan/build/check/edit`。
