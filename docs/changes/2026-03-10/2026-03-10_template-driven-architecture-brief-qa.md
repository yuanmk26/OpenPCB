# 2026-03-10 模板化架构问答系统（board_class JSON + 选项交互）

## 1. 变更前问题

- 架构补全仍是固定题目与自由文本输入，未按板卡类型模板化管理。
- 交互缺少结构化选项引导，用户输入质量波动较大。
- 会话状态未记录模板版本与题目选项上下文，难以追踪和复现。

## 2. 变更内容

- 将 `ArchitectureBriefCollector` 重构为模板驱动：
  - 按 `board_class` 加载模板 JSON，缺失时回退 `generic.json`。
  - 模板包含：`template_id`、`version`、`required_fields`、`questions`。
  - 每题固定 3 个选项 + 自定义提示，并支持最小长度校验。
- 新增模板目录与模板文件：
  - `openpcb/agent/templates/architecture_brief/generic.json`
  - `openpcb/agent/templates/architecture_brief/mcu_core.json`
  - `openpcb/agent/templates/architecture_brief/power.json`
- 升级 CLI 补全过程：
  - 显示格式：`问题 i/N` + `1/2/3/4(自定义)`。
  - 输入 `1/2/3` 映射选项值；输入 `4` 进入自定义输入等待态；直接文本按自定义处理。
  - 无效/过短答案立即重问并提示。
- 扩展会话状态：
  - `brief_template_id`
  - `brief_template_version`
  - `brief_field_options`
  - `brief_expect_custom_input`
- 扩展规划输入与元数据：
  - plan payload 新增：`architecture_brief_template_id`、`architecture_brief_template_version`
  - `project.metadata` 注入模板 id/version，保留已有 `classification` 与 `architecture_brief`。

## 3. 影响范围

- 修改文件：
  - `openpcb/agent/brief_collector.py`
  - `openpcb/agent/session.py`
  - `openpcb/agent/runtime.py`
  - `openpcb/cli/commands/chat.py`
  - `tests/agent/test_brief_collector.py`
  - `tests/cli/test_chat.py`
- 新增文件：
  - `openpcb/agent/templates/architecture_brief/generic.json`
  - `openpcb/agent/templates/architecture_brief/mcu_core.json`
  - `openpcb/agent/templates/architecture_brief/power.json`
  - `docs/changes/2026-03-10/2026-03-10_template-driven-architecture-brief-qa.md`

## 4. 验证结果

- 语法校验通过：
  - `python -m py_compile openpcb/agent/brief_collector.py openpcb/agent/session.py openpcb/agent/runtime.py openpcb/cli/commands/chat.py tests/agent/test_brief_collector.py tests/cli/test_chat.py`
- 自动化测试尝试执行：
  - `python -m pytest tests/agent/test_brief_collector.py tests/cli/test_chat.py`
- 结果：当前环境缺少 `pytest`（`No module named pytest`），未能完成本地运行。

## 5. 下一步建议

1. 安装 pytest 后运行新增测试，重点确认“4=自定义输入等待态”与模板回退逻辑。
2. 为 `sensor_io`、`connectivity` 增加专属模板，减少对 generic 回退依赖。
3. 后续加入“修改已回答字段”命令，增强复用场景下的可编辑性。
