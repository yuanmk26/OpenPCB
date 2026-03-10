# OpenPCB Architecture Docs

本目录用于沉淀 OpenPCB 架构，统一采用“现状（Current）+目标（Target）”双视图表达，避免只写理想设计或只写历史实现。

## 推荐阅读顺序

1. `system-architecture.md`：全局分层、端到端主流程、产物契约。
2. `agent-architecture.md`：Agent 编排边界、执行模型、对话路由与日志。
3. `pcb-pipeline-architecture.md`：PCB 主链路（IR、模板/规则、导出接口）实现规范。

## 文档标注规范

- 每个核心章节都应包含：背景、现状、目标、接口、数据流、失败模式、测试映射、下一步。
- 状态值只允许：`已实现` / `进行中` / `未开始`。
- Mermaid 图建议使用 `subgraph Current` 与 `subgraph Target` 明确双视图。

## 维护规则

- 文档必须基于当前仓库代码事实，不得把未实现能力写成已实现。
- 目标视图应与 `docs/project/TODO_LIST.md` 方向一致，不引入冲突术语。
- 发生架构相关变更时，必须同时更新本目录与 `docs/changes/` 记录。
- 每次任务完成后，默认执行 `git add` + `git commit` + `git push`；如推送失败需保留失败信息并告知原因。
