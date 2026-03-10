# 2026-03-10 架构文档重构：聚焦 PCB 主链路

## 变更前问题
- 架构文档偏向 Runtime/LLM 接入，PCB 主链路（IR、模板/规则、导出）描述不足。
- 新读者无法直接从文档理解“谁生成 IR、谁消费 IR、KiCad 导出在哪一层”。
- 文档缺少统一的 Current/Target 双视图表达，容易把现状与目标混淆。

## 变更内容
- 重写 `docs/architecture/agent-architecture.md`：
  - 引入 `Conversation Orchestrator / Runtime / Tools / Domain adapters` 分层。
  - 用 Current + Target 双视图说明 Agent 边界与演进。
  - 明确 Agent 只做决策与编排，不承载 KiCad 格式细节。
- 重写 `docs/architecture/system-architecture.md`：
  - 升级为 7 层总体架构（CLI、Conversation、Runtime、IR/Schema、PCB Domain、IO/Exporter、Config/LLM）。
  - 增加端到端双视图主流程图与“中间产物 + 最终产物”契约。
- 新增 `docs/architecture/pcb-pipeline-architecture.md`：
  - 专门定义 PCB 主链路阶段：Intent Parser、IR Builder/Normalizer、Planner、Builder、Exporter、Checker。
  - 明确 v1 接口：`parse/plan/build/export/check`。
  - 标注实现状态（已实现/进行中/未开始）。
- 更新 `docs/architecture/README.md`：
  - 增加推荐阅读顺序与双视图标注规范。

## 影响范围
- 仅文档变更，不修改代码行为与 CLI 接口。
- 影响读者理解路径：可直接按系统 -> Agent -> PCB pipeline 顺序建立全局认知。

## 验证结果
- 文件存在：
  - `docs/architecture/README.md`
  - `docs/architecture/agent-architecture.md`
  - `docs/architecture/system-architecture.md`
  - `docs/architecture/pcb-pipeline-architecture.md`
- 关键内容检查通过：
  - 双视图（Current/Target）
  - IR 主对象与阶段接口
  - Build/Export 职责分界
  - 与 `docs/project/TODO_LIST.md` 的状态体系一致

## 下一步建议
1. 在代码层落地 `BuildBundle` 与 exporter 分层，消除 builder 直写文件耦合。
2. 增加 IR normalizer 阶段并接入 `plan/build` 共享。
3. 将 checker 升级为规则引擎并按 IR 执行。

## 后续补充

- 基于最新架构讨论，补充 `mode/action/toolchain` 解耦原则。
- 明确 `mode` 是 PCB 工作视角，不是硬编码线性流程状态。
- 新增 `docs/architecture/mode-action-architecture.md`，用于承接后续实现。
