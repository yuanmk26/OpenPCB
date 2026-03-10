# 2026-03-10 分类后架构信息补全门禁（v1）

## 1. 变更前问题

- 分类完成后，`/yes` 会直接进入 `plan`，缺少架构层关键信息补全步骤。
- 规划输入中没有统一沉淀“板卡目标/电源/接口/约束/成本”等基础架构信息。
- 用户在信息不足时仍可触发规划，导致后续产出完整性不稳定。

## 2. 变更内容

- 新增 `ArchitectureBriefCollector`，实现 6 个必填项的逐题收集与缺失项计算。
- 在会话状态中新增补全状态字段：
  - `architecture_brief`
  - `brief_required_fields`
  - `brief_pending_field`
  - `brief_completed`
- 在 `chat` 文本路由引入补全门禁状态机：
  - `classified`：分类后确认是否进入补全
  - `brief_collecting`：逐题问答收集（单轮单问）
  - `ready_to_plan`：信息齐备，等待 `/yes` 进入规划
- ` /yes` 与 `/no` 语义增强：
  - `/yes` 在不同阶段执行对应动作（进入补全 / 门禁检查 / 执行规划）
  - `/no` 在补全过程可取消 pending，并清空当前补全过程状态（保留已填答案）
- 规划上下文注入：
  - `plan` payload 增加 `architecture_brief`
  - runtime 将 `classification` 与 `architecture_brief` 写入 `project.metadata`

## 3. 影响范围

- 新增文件：`openpcb/agent/brief_collector.py`
- 修改文件：
  - `openpcb/agent/session.py`
  - `openpcb/agent/runtime.py`
  - `openpcb/cli/commands/chat.py`
  - `tests/cli/test_chat.py`
- 新增测试：`tests/agent/test_brief_collector.py`
- 新增变更记录：`docs/changes/2026-03-10/2026-03-10_architecture-brief-gate-v1.md`

## 4. 验证结果

- 语法检查通过：
  - `python -m py_compile openpcb/agent/brief_collector.py openpcb/agent/session.py openpcb/agent/runtime.py openpcb/cli/commands/chat.py tests/agent/test_brief_collector.py tests/cli/test_chat.py`
- 自动化测试尝试执行：
  - `python -m pytest tests/agent/test_brief_collector.py tests/cli/test_chat.py`
- 结果：当前环境缺少 `pytest`（`No module named pytest`），未能完成本地测试运行。

## 5. 下一步建议

1. 安装 pytest 后运行新增测试，确认补全门禁和元数据注入路径通过。
2. 后续可按 `board_class` 自定义补全问题模板（保持字段一致，提升问答相关性）。
3. 在 `/status` 中补充 brief 进度展示，便于用户查看当前缺失项。
