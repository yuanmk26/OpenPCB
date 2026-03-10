# 2026-03-10 分类驱动会话入口（首版）

## 1. 变更前问题

- `openpcb chat` 的文本输入分支默认走 LLM 对话，缺少“板卡需求识别 -> 分类 -> 确认”前置链路。
- 无法在首句“我想设计一个 XXX 板卡”时给出结构化分类（`board_class + board_family`）。
- 分类结果未进入规划上下文，`plan` 阶段无法感知会话路由层的分类结论。

## 2. 变更内容

- 新增 `RequirementClassifier`（规则分类，独立于现有 parser）：
  - 输入：`user_text`
  - 输出：`ClassificationResult`
  - 字段：`board_class`、`board_family`、`confidence`、`reason`、`should_route`
  - 首版类别：`mcu_core`、`power`、`sensor_io`、`connectivity`，并保留 `other` 低置信度兜底。
- 在 `chat` 文本路由接入分类阶段：
  - 当文本命中“设计板卡”意图时先分类。
  - 高置信度（>= 0.6）创建待确认 `plan`（`/yes` 执行，`/no` 取消）。
  - 低置信度给出澄清提示，不直接执行 plan。
- 扩展 `PendingAction`：新增 `metadata`，用于携带分类结果。
- 将分类结果注入 planner 上下文：
  - `chat -> runtime` 传入 `classification`
  - `runtime` 在 `plan` 输出的 `project.metadata.classification` 保留分类信息。

## 3. 影响范围

- 新增文件：`openpcb/agent/classifier.py`
- 修改文件：
  - `openpcb/agent/session.py`
  - `openpcb/cli/commands/chat.py`
  - `openpcb/agent/runtime.py`
- 新增测试：`tests/agent/test_classifier.py`
- 修改测试：`tests/cli/test_chat.py`
- 新增变更记录：`docs/changes/2026-03-10/2026-03-10_conversation-entry-requirement-classification-v1.md`

## 4. 验证结果

- 语法校验通过：
  - `python -m py_compile openpcb/agent/classifier.py openpcb/agent/session.py openpcb/agent/runtime.py openpcb/cli/commands/chat.py tests/agent/test_classifier.py tests/cli/test_chat.py`
- 自动化测试尝试执行：
  - `python -m pytest tests/agent/test_classifier.py tests/cli/test_chat.py`
- 结果：当前环境缺少 `pytest`（`No module named pytest`），未完成本地测试运行。

## 5. 下一步建议

1. 安装测试依赖后重跑新增用例，确认分类路由与确认链路在 CI 通过。
2. 后续将 `board_class` 与 mode policy 连接，逐步替代硬编码 task 路由。
3. 若需要更稳健分类，可在规则层增加别名字典与冲突优先级策略。
