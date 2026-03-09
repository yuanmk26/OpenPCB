# OpenPCB TODO List (Agent-First)

> 主任务源文件。  
> 目标：以单 Agent 循环 + 工具调用方式，完成 `init -> plan -> build -> check -> edit -> build` 可回放闭环。

---

## 1. 状态说明

- `已完成`：核心验收标准满足，可用于下一阶段输入。
- `进行中`：命令或能力已接入，但业务深度不足。
- `未开始`：实现尚未落地。

---

## 2. 当前接口契约

### CLI

- `openpcb init <project_name> [--dir]`
- `openpcb plan "<requirement>" [--project-name] [--project-dir]`
- `openpcb build <project.json|project_dir>`
- `openpcb generate <project.json|project_dir>`（兼容别名，已弃用）
- `openpcb check <project.json|project_dir>`
- `openpcb edit <project.json|project_dir> "<instruction>"`

### Agent Runtime（内部）

- `run(task_type, input_payload, options) -> RunResult`
- Tool 执行语义：`observe -> plan -> act(tool) -> reflect -> finalize`
- 运行轨迹：`logs/agent-run-*.jsonl`

---

## 3. Milestones

## Milestone A: Foundation

### A1 包与 CLI 基础
- 状态：`已完成`
- 输入：本地仓库源码
- 输出：可安装包、可运行 CLI 主入口
- 依赖：无
- 验收标准：`pip install -e .` 后 `openpcb --help` 正常
- 测试点：`tests/cli/test_help.py`、`tests/cli/test_version.py`

### A2 项目初始化命令
- 状态：`已完成`
- 输入：项目名
- 输出：`project.json`、`plan.md`、`output/`、`logs/`
- 依赖：A1
- 验收标准：`openpcb init demo` 创建目录结构
- 测试点：`tests/cli/test_init.py`

### A3 错误体系与基础 I/O
- 状态：`已完成`
- 输入：路径/JSON 载荷
- 输出：统一异常、项目读写能力
- 依赖：A1
- 验收标准：`project_loader/project_saver` 可读写并报错清晰
- 测试点：CLI 路径错误时返回非 0

---

## Milestone B: Plan Agent

### B1 Intent Parser
- 状态：`已完成`
- 输入：自然语言需求
- 输出：结构化意图（模块候选、板卡族）
- 依赖：A3
- 验收标准：关键词可映射常见模块（STM32/USB/LED/UART）
- 测试点：新增 parser 单测（待补）

### B2 Planner（规则版）
- 状态：`已完成`
- 输入：Intent
- 输出：`ProjectSpec`（含 modules）
- 依赖：B1
- 验收标准：可生成合法 `project.json`
- 测试点：`tests/cli/test_plan_build.py::test_plan_generates_project_json_and_plan_md`

### B3 Plan 命令落盘
- 状态：`已完成`
- 输入：需求文本 + 项目目录
- 输出：`project.json`、`plan.md`、trace 日志
- 依赖：B2
- 验收标准：`openpcb plan ...` 成功并落盘
- 测试点：同 B2

---

## Milestone C: Build Agent

### C1 Builder 工具
- 状态：`已完成`
- 输入：`project.json`
- 输出：`output/kicad/*`、`output/bom.json`、`output/netlist.json`、`output/reports/build-report.md`
- 依赖：B3
- 验收标准：`openpcb build <project_dir>` 产物落盘
- 测试点：`tests/cli/test_plan_build.py::test_build_generates_artifacts`

### C2 Generate 兼容层
- 状态：`已完成`
- 输入：与 build 相同
- 输出：调用 build，输出 deprecated 提示
- 依赖：C1
- 验收标准：`openpcb generate` 与 build 产物一致
- 测试点：`tests/cli/test_plan_build.py::test_generate_alias_for_build`

### C3 Build 深化（真实 KiCad writer）
- 状态：`未开始`
- 输入：ProjectSpec + 模板
- 输出：可在 KiCad 中可视化/可编辑的工程
- 依赖：C1
- 验收标准：包含可验证元件和网络连接
- 测试点：kicad 文件结构校验 + 快照测试

---

## Milestone D: Check Agent

### D1 检查规则接口
- 状态：`进行中`
- 输入：ProjectSpec
- 输出：诊断列表（error/warn/info）
- 依赖：B3
- 验收标准：统一规则执行入口
- 测试点：规则引擎单测

### D2 首批工程规则
- 状态：`未开始`
- 输入：ProjectSpec
- 输出：至少 5 条有效规则
- 依赖：D1
- 验收标准：可识别缺电源、缺接口等场景
- 测试点：场景化 fixtures

### D3 Check 命令报告
- 状态：`进行中`
- 输入：项目路径
- 输出：`output/reports/check-report.md`
- 依赖：D1
- 验收标准：统计错误/告警并可读输出
- 测试点：新增 CLI `check` 测试（待补）

---

## Milestone E: Edit Agent

### E1 编辑意图解析
- 状态：`进行中`
- 输入：编辑指令文本
- 输出：结构化 edit action
- 依赖：B1
- 验收标准：识别 add/remove/replace/update 基本动作
- 测试点：parser edit 单测（待补）

### E2 ProjectSpec 修改器
- 状态：`进行中`
- 输入：ProjectSpec + edit action
- 输出：更新后的 ProjectSpec
- 依赖：E1
- 验收标准：修改后 schema 合法
- 测试点：executor 单测（待补）

### E3 Edit 命令落盘
- 状态：`进行中`
- 输入：项目路径 + 指令
- 输出：更新 `project.json` + `output/reports/edit-report.md`
- 依赖：E2
- 验收标准：`openpcb edit ...` 可重跑 build
- 测试点：新增 CLI `edit` 测试（待补）

---

## Milestone F: Release

### F1 示例工程
- 状态：`未开始`
- 输入：固定需求模板
- 输出：至少 3 个可复现 example
- 依赖：C3, D3, E3
- 验收标准：示例全链路可跑通
- 测试点：examples 集成测试

### F2 文档与发布
- 状态：`进行中`
- 输入：当前实现与命令行为
- 输出：README、架构文档、变更日志
- 依赖：F1
- 验收标准：新用户可按文档完成一次端到端运行
- 测试点：文档命令 smoke test

---

## 4. 下一阶段优先级（从现在开始）

1. D1/D2：把 check 从“基本检查器”升级到规则引擎。
2. E1/E2：把 edit 从关键词拼装升级为标准化 action pipeline。
3. C3：替换 mock builder 为真实模板+writer 输出。
4. 补齐测试矩阵：parser/planner/check/edit 单测 + e2e。

---

## 5. Done Definition（v0.1）

- [x] `openpcb init` 可创建项目
- [x] `openpcb plan "<需求>"` 可生成 `project.json` 和 `plan.md`
- [x] `openpcb build project.json|project_dir` 可生成工程产物
- [x] `openpcb generate` 兼容层可用并提示弃用
- [ ] `openpcb check` 完成规则化检查（当前仅基础检查）
- [ ] `openpcb edit` 完成结构化增量修改（当前为规则版）
- [ ] 至少 3 个 demo 可复现
- [ ] 关键路径具备完整测试覆盖（当前覆盖 init/plan/build/generate）

---

## Milestone G: Model Integration

### G1 LLM 配置层
- 状态：`进行中`
- 输入：`openpcb.config.toml`
- 输出：运行时可读配置对象（provider/model/api_key/base_url/timeout/max_retries）
- 依赖：A3
- 验收标准：缺 key 且未开启 mock 时，`plan` 明确报错退出
- 测试点：`tests/agent/test_config_loader.py`

### G2 OpenAI-Compatible Client（OpenAI/DeepSeek）
- 状态：`进行中`
- 输入：planner prompt + requirement
- 输出：可解析的 JSON 文本响应
- 依赖：G1
- 验收标准：请求成功可返回 content/token，HTTP 错误可映射为结构化异常
- 测试点：`tests/agent/test_openai_client.py`

### G3 Planner JSON 约束与解析
- 状态：`进行中`
- 输入：LLM 原始文本
- 输出：`ProjectSpec`
- 依赖：G2
- 验收标准：非法 JSON 明确报错，合法 JSON 可通过 schema 校验
- 测试点：`tests/agent/test_planner_json_parse.py`

### G4 Runtime/CLI 接入
- 状态：`进行中`
- 输入：`openpcb plan ...`
- 输出：真实模型规划结果 + trace（含 provider/model/token/latency）
- 依赖：G3
- 验收标准：支持 `--provider --model --config`；失败直接退出（无 mock 自动回退）
- 测试点：`tests/cli/test_plan_build.py::test_plan_without_api_key_fails`

### G5 测试与安全
- 状态：`进行中`
- 输入：mock client/失败场景
- 输出：单测覆盖 + `.gitignore` 密钥保护
- 依赖：G1, G2, G3, G4
- 验收标准：`openpcb.config.toml` 不入库，核心模型路径有测试覆盖
- 测试点：`tests/agent/*` + `tests/cli/*`


---

## Milestone H: Interactive CLI

### H1 chat 命令骨架
- 状态：`进行中`
- 输入：`openpcb chat --project-dir <dir> [--config ...]`
- 输出：可持续输入的 REPL 会话
- 依赖：B3, C1, D3, E3
- 验收标准：支持自然语言 plan 与 `/help` `/exit`
- 测试点：`tests/cli/test_chat.py`

### H2 会话状态与日志
- 状态：`进行中`
- 输入：会话动作序列
- 输出：`logs/session-*.jsonl` + 内存状态对象
- 依赖：H1
- 验收标准：可记录 session_id、项目路径、动作历史、结果摘要
- 测试点：`tests/agent/test_session.py`

### H3 交互动作路由（plan/build/check/edit）
- 状态：`进行中`
- 输入：REPL 指令（文本、`/build`、`/check`、`/edit ...`）
- 输出：对应 runtime 执行结果
- 依赖：H1, H2
- 验收标准：用户可在单会话手动推进完整链路
- 测试点：`tests/cli/test_chat.py::test_chat_sequence_plan_build_check_exit`

### H4 可用性与错误恢复
- 状态：`进行中`
- 输入：异常场景（未 plan 即 build、模型失败）
- 输出：清晰提示且会话不中断
- 依赖：H3
- 验收标准：错误不导致 REPL 崩溃，允许继续输入或退出
- 测试点：`tests/cli/test_chat.py::test_chat_build_before_plan_shows_hint`

### H5 交互文档与示例
- 状态：`进行中`
- 输入：chat 命令行为
- 输出：README 交互式使用小节与示例
- 依赖：H1-H4
- 验收标准：新用户可按文档完成一次交互式会话
- 测试点：README 命令 smoke
