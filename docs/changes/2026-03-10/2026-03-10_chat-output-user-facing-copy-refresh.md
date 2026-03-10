# 2026-03-10 chat 输出文案用户化改造

## 1. 变更前问题

- chat 交互输出偏工程日志风格（如 `Conclusion`、`planner mock`、`Trace`），普通用户理解成本高。
- 分类确认提示直接暴露 `mcu_core/stm32` 这类内部标签，不够友好。
- 成功/失败反馈缺少面向用户的自然表达，容易造成“功能完成但用户看不懂”的体验问题。

## 2. 变更内容

- 重写 chat presenter 文案为用户可读版本：
  - 成功提示统一为 `已完成：<action>`。
  - `plan/build/check/edit` 分别输出更直观的结果说明。
  - 默认成功输出不再展示模型/token/trace 等开发细节。
- 优化确认与决策文案：
  - 写盘确认改为中文说明（`/yes` 继续、`/no` 取消）。
  - 决策摘要从 `Decision: ...` 改为 `已识别操作：...`。
- 优化需求分类确认提示：
  - 将 `board_class` 映射为用户标签（如 `mcu_core -> 单片机核心板`）。
  - 显示为 `已识别需求：单片机核心板（STM32）`，并附中文确认引导。
  - 低置信度场景输出中文澄清提示。
- 同步更新 CLI 测试断言到新文案。

## 3. 影响范围

- 修改文件：`openpcb/cli/presenter.py`
- 修改文件：`openpcb/cli/commands/chat.py`
- 修改文件：`tests/cli/test_chat.py`
- 新增文件：`docs/changes/2026-03-10/2026-03-10_chat-output-user-facing-copy-refresh.md`

## 4. 验证结果

- 语法检查通过：
  - `python -m py_compile openpcb/cli/presenter.py openpcb/cli/commands/chat.py tests/cli/test_chat.py`
- 自动化测试尝试执行：
  - `python -m pytest tests/cli/test_chat.py`
- 结果：当前环境缺少 `pytest`（`No module named pytest`），未能本地跑测。

## 5. 下一步建议

1. 安装 pytest 后执行 `tests/cli/test_chat.py`，确认文案回归通过。
2. 若后续要兼顾开发调试，可增加 `--verbose` 输出开关，把 trace 和模型细节放到 verbose 模式。
