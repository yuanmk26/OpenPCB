# 2026-03-10 架构文档目录与总览落地

## 变更前问题
- `docs/` 目录只有 `changes/`，缺少专门承载架构说明的目录。
- Agent 架构与系统总体架构信息分散在代码和历史变更记录中，不利于新成员快速建立全局理解。

## 变更内容
- 新增架构文档目录：`docs/architecture/`
- 新增目录入口文档：`docs/architecture/README.md`
- 新增 Agent 架构文档：`docs/architecture/agent-architecture.md`
- 新增系统总体架构文档：`docs/architecture/system-architecture.md`
- 更新 `docs/README.md`，将 `architecture/` 纳入文档目录规范，并补充维护规则。

## 影响范围
- 仅文档变更，不涉及 CLI 参数、运行时逻辑、数据结构与模型调用行为。
- 文档读者可直接通过 `docs/architecture/` 获取当前实现架构，不再依赖散落代码阅读。

## 验证结果
- 已创建并确认以下文件存在：
  - `docs/architecture/README.md`
  - `docs/architecture/agent-architecture.md`
  - `docs/architecture/system-architecture.md`
- `docs/README.md` 已包含 `architecture/` 目录说明与维护规则。
- 架构文档内容已对齐当前实现：`runtime/chat/planner/builder/checker/config`。

## 下一步建议
1. 在后续重大架构调整时，先更新 `docs/architecture/` 再提交代码，保持“设计与实现”同步。
2. 当 check/build/edit 深化到下一阶段时，在文档中将状态从“进行中”切到“已实现”并补具体能力边界。
3. 可在后续补充 `architecture/decision-log.md`，记录关键架构决策与取舍。
