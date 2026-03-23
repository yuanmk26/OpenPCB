# 2026-03-23 Agent-Team Architecture Refactor

## 变更前问题

- `docs/architecture/system-architecture.md` 与 `docs/architecture/directory_tree.md` 存在历史失真/乱码内容，且部分叙述与当前仓库事实不一致。
- Agent 架构文档仍偏向旧的单体任务链路，未明确 `pi-mono + agent-team` 的主从协作边界。
- 缺少独立的项目知识库文档承载“项目事实汇总与同步维护”职责。

## 变更内容

- 重写 `docs/architecture/agent-architecture.md`：
  - 采用 Current + Target 双视图。
  - 明确 `Master Agent + 3 Worker Agents`（Project-Info/SDL/Schematic）职责边界。
  - 新增主从协作数据流图。
  - 新增概念级协作契约 `TaskEnvelope` 与 `WorkerResult`。
- 重写 `docs/architecture/system-architecture.md`：
  - 校正系统叙述到 `pi-mono + agent-team` 方向。
  - 增加 Agent Team 在系统中的位置与端到端流转。
  - 明确 SDL 仍为上游语义契约。
- 重写 `docs/architecture/directory_tree.md`：
  - 清理旧快照与乱码。
  - 改为基于当前仓库事实的目录快照。
  - 纳入 `docs/project/knowledge-base.md` 落点。
- 新增 `docs/project/knowledge-base.md`：
  - 定义项目知识库最小模板（目标、能力、约束、里程碑、风险、待决策项）。
  - 指定 `Project-Info Agent` 为维护责任角色。
  - 增加信息来源优先级与更新触发条件。

## 影响范围

- 文档范围：
  - `docs/architecture/agent-architecture.md`
  - `docs/architecture/system-architecture.md`
  - `docs/architecture/directory_tree.md`
  - `docs/project/knowledge-base.md`
- 变更记录：
  - `docs/changes/2026-03-23/2026-03-23_agent-team-architecture-refactor.md`
- 不涉及运行时代码与接口实现变更。

## 验证结果

- 术语一致性：架构文档统一使用 `SDL`，未引入 `DLS` 新术语。
- 架构一致性：文档统一采用 `pi-mono + agent-team` 方向，不再以 Python 绑定作为前提叙述。
- 目录事实性：`directory_tree.md` 按当前仓库实际目录重写，并包含新增知识库文档落点。
- 交叉一致性：新增知识库文档与架构文档职责描述一致，且与 `docs/sdl/README.md` 的 SDL 定位不冲突。

## 下一步建议

1. 在运行时设计文档中补充主从任务生命周期与失败恢复策略。
2. 为 SDL Agent 与 Schematic Agent 增加“语义缺口清单”与收敛节奏说明。
3. 后续若新增员工 agent，建议在 `agent-architecture.md` 增加版本化角色目录。
