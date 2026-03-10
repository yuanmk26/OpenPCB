# OpenPCB TODO（Architecture-Aligned）

> 主任务源文件。  
> 目标：按当前架构推进 OpenPCB，从“可用命令链”演进到“mode-action 驱动的稳定工程流水线”。

---

## 1. 状态说明

- `已完成`：能力已落地并有可复用入口或测试。
- `进行中`：能力已接入，但深度或边界尚不完整。
- `未开始`：尚未进入实现。

---

## 2. 当前架构基线（2026-03）

### 2.1 已落地

- CLI 命令链：`init / plan / build / check / edit / chat`。
- 会话能力：`openpcb chat` REPL、会话日志、基础动作路由。
- IR 与核心领域对象：`ProjectSpec / ModuleSpec / NetSpec / Component`。
- Plan/Build 基础闭环：可生成 `project.json`、`plan.md` 和基础构建产物。
- CI 基线：PR/main 自动执行 `ruff + pytest + build`。

### 2.2 关键缺口

- 顶层仍以 `task_type` 驱动，`mode -> action -> toolchain` 尚未成为主执行轴。
- PCB pipeline 中 `BuildBundle` 与 `Exporter` 尚未独立，builder 仍直接写盘。
- Checker 仍是基础规则集合，缺少可扩展规则引擎与分层报告。
- Edit 仍以规则/关键词驱动，尚未完成结构化 action pipeline。

---

## 3. 架构对齐任务（Roadmap）

## A. Conversation 与编排层

### A1 Conversation-first 默认入口（`openpcb` 直进 shell）
- 状态：`已完成`
- 目标：将默认入口从 help 转为对话 shell，`openpcb chat` 作为兼容别名。
- 验收标准：`openpcb` 无参数进入会话；可通过 `/help` 查看命令与模式。
- 测试点：新增 CLI 入口行为测试。

### A2 Conversation Router（chat vs task 判定）
- 状态：`进行中`
- 目标：从文本路由到 `ChatReply` 或 `WorkProposal`，减少误触发写盘任务。
- 验收标准：自然对话不触发 plan/build/check/edit；任务意图可稳定识别。
- 测试点：会话路由单测 + REPL 场景测试。

### A3 WorkProposal 确认机制
- 状态：`未开始`
- 目标：任务执行前支持显式确认，尤其是写盘动作。
- 验收标准：`plan/build/edit` 等动作在策略要求下必须确认后执行。
- 测试点：会话确认流测试。

---

## B. Mode-Action 核心模型

### B1 Session 增加 `current_mode`
- 状态：`已完成`
- 目标：在会话状态里持久化当前工作视角。
- 验收标准：会话日志可追踪 mode 变化；重入会话可恢复 mode。
- 测试点：`tests/agent/test_session.py` 扩展。

### B2 Mode Router + Action Resolver
- 状态：`未开始`
- 目标：落地 `mode != action != tool`，替代粗粒度 task 路由。
- 验收标准：至少支持 v1 范围的 `(mode, action)` 合法性校验与拒绝机制。
- 测试点：模式路由、非法组合拒绝、动作归一化测试。

### B3 Mode Policy 到 Runtime 解析
- 状态：`未开始`
- 目标：从 `resolve(mode, action, context) -> toolchain` 驱动 runtime 执行。
- 验收标准：runtime 不再硬编码 PCB 阶段步骤链。
- 测试点：policy resolution 与 runtime 解耦测试。

---

## C. PCB Pipeline（IR -> Build -> Export -> Check）

### C1 IR Normalizer
- 状态：`未开始`
- 目标：在 planner 前引入结构归一化层，统一上下文输入。
- 验收标准：intent 与 project context 进入统一 `ProjectSpec` 规范化流程。
- 测试点：normalizer 输入输出与异常路径测试。

### C2 BuildBundle 改造
- 状态：`未开始`
- 目标：builder 从“直接写盘”改为“生成中间构建对象”。
- 验收标准：`build(project_spec) -> BuildBundle` 合同稳定。
- 测试点：builder 单测 + CLI 回归测试。

### C3 Exporter 分层
- 状态：`未开始`
- 目标：新增 exporter 统一输出 KiCad/BOM/Netlist/report。
- 验收标准：`export(build_bundle, target)` 接口可替代当前 builder 写盘。
- 测试点：产物路径、文件完整性、失败可重试测试。

### C4 Checker 规则引擎化
- 状态：`进行中`
- 目标：从基础检查演进为可扩展规则接口与分级报告。
- 验收标准：支持规则注册、分级诊断（error/warn/info）、可追踪 rule id。
- 测试点：规则引擎单测 + `check` CLI 场景测试。

---

## D. Plan/Edit 与模型集成

### D1 Planner JSON 约束稳定化
- 状态：`进行中`
- 目标：提高 LLM 输出可解析率与错误可诊断性。
- 验收标准：非法 JSON 明确报错；合法 JSON 100% 通过 schema 校验路径。
- 测试点：`tests/agent/test_planner_json_parse.py`。

### D2 Edit Action Pipeline
- 状态：`进行中`
- 目标：将 edit 从关键词拼装升级为结构化 action 执行链。
- 验收标准：支持 add/remove/replace/update 的结构化修改与回写。
- 测试点：`tests/cli/test_check_edit.py` 扩展 + executor 单测。

### D3 Provider 抽象完善（OpenAI-compatible）
- 状态：`进行中`
- 目标：稳定 provider/model/config 选择、异常映射与重试策略。
- 验收标准：缺 key、HTTP 错误、超时场景均返回一致的结构化错误。
- 测试点：`tests/agent/test_config_loader.py`、`tests/agent/test_openai_client.py`。

---

## E. 质量与发布

### E1 测试矩阵补齐
- 状态：`进行中`
- 目标：覆盖 mode/action 路由、pipeline 分层、check/edit 核心分支。
- 验收标准：核心链路具备单测 + CLI 集成测试。
- 测试点：`tests/agent/*` + `tests/cli/*`。

### E2 示例工程与回放
- 状态：`未开始`
- 目标：提供不少于 3 个可复现示例工程（含 logs 与产物）。
- 验收标准：可一键复现 `init -> plan -> build -> check -> edit -> build`。
- 测试点：examples e2e smoke。

### E3 CD 发布工作流
- 状态：`未开始`
- 目标：基于 tag(`v*`) 自动创建 GitHub Release 并上传构建产物。
- 验收标准：tag 推送后 release 产物完整可下载。
- 测试点：workflow dry-run / release 验证。

---

## 4. 近阶段优先级（P0 -> P2）

1. P0：B2/B3（先打通 mode-action 主轴，避免继续加重 task_type 技术债）。
2. P0：C2/C3（解耦 builder 与 exporter，建立可演进流水线边界）。
3. P1：C4/D2（补强 check/edit 的工程可用性）。
4. P1：A2/A3（降低会话误触发任务风险）。
5. P2：E2/E3（示例固化、CD 自动化）。

---

## 5. Definition of Done（架构版本）

- [x] CLI 与会话入口可用，基础任务链能跑通。
- [x] IR schema 与 `plan/build` 基础产物能力可用。
- [x] CI 基线（ruff/pytest/build）已上线。
- [ ] 会话层完成 `chat/work` 分离与 `WorkProposal` 确认机制。
- [ ] mode-action-policy 成为 runtime 的主执行模型。
- [ ] pipeline 完成 `BuildBundle + Exporter` 分层。
- [ ] checker/edit 形成结构化、可扩展执行链。
- [ ] 至少 3 个可复现 demo 与 CD 发布流程打通。
