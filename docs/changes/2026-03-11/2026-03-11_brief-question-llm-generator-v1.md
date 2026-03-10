# 2026-03-11 模板字段约束 + LLM动态提问（v1）

## 1. 变更前问题

- 架构补全问答虽已模板化，但问题文案完全固定，语境适配较弱。
- 同一字段重问时会重复生成类似文案，缺少缓存复用。
- 失败场景下缺少显式“生成失败回退模板问句”的可测试保障。

## 2. 变更内容

- 新增 `BriefQuestionGenerator`，将“问句生成”从字段约束中解耦：
  - 输入：`board_class`、`board_family`、当前字段信息、模板问句、选项、已填摘要、缺失字段。
  - 输出：仅一条自然语言问题文本，不参与字段顺序和选项决策。
- 新增提问 prompt 文件（文件化管理）：
  - `openpcb/agent/prompts/brief_question_system.txt`
  - `openpcb/agent/prompts/brief_question_user_template.txt`
- 在 `chat` 的 `brief_collecting` 流程接入动态问句：
  - Collector 仍负责字段顺序、门禁、选项。
  - LLM 成功时显示动态问句；失败时自动回退模板问句。
- 新增问句缓存机制：
  - `ChatSession.brief_question_cache`
  - 缓存键：`template_id + field + brief_hash + board_class + board_family`
  - 同题同上下文重问优先命中缓存，减少重复调用。
- 保持兼容边界：
  - `/yes` 门禁、`/no` 取消、`1/2/3/4` 协议不变。
  - `project.metadata` 继续保留 `classification`、`architecture_brief`、模板 id/version。

## 3. 影响范围

- 修改文件：
  - `openpcb/agent/brief_collector.py`
  - `openpcb/agent/session.py`
  - `openpcb/cli/commands/chat.py`
  - `openpcb/agent/templates/architecture_brief/generic.json`
  - `openpcb/agent/templates/architecture_brief/mcu_core.json`
  - `openpcb/agent/templates/architecture_brief/power.json`
- 新增文件：
  - `openpcb/agent/brief_question_generator.py`
  - `openpcb/agent/prompts/brief_question_system.txt`
  - `openpcb/agent/prompts/brief_question_user_template.txt`
  - `tests/agent/test_brief_question_generator.py`
  - `tests/cli/test_brief_question_cache.py`
  - `docs/changes/2026-03-11/2026-03-11_brief-question-llm-generator-v1.md`

## 4. 验证结果

- 语法校验通过：
  - `python -m py_compile openpcb/agent/brief_collector.py openpcb/agent/brief_question_generator.py openpcb/agent/session.py openpcb/cli/commands/chat.py tests/agent/test_brief_question_generator.py tests/cli/test_brief_question_cache.py`
- JSON 校验通过：
  - `python - <<'PY' ... json.load(...) ... PY`
- 自动化测试尝试执行：
  - `python -m pytest tests/agent/test_brief_question_generator.py tests/cli/test_brief_question_cache.py tests/agent/test_brief_collector.py tests/cli/test_chat.py -q`
- 结果：当前环境缺少 `pytest`（`No module named pytest`），未完成本地测试运行。

## 5. 下一步建议

1. 安装 `pytest` 后优先运行 `tests/cli/test_chat.py` 验证真实对话链路。
2. 为 `BriefQuestionGenerator` 增加长度与语气约束测试，避免问句过长。
3. 后续可增加“字段重写命令”，支持用户补全后回改答案。
