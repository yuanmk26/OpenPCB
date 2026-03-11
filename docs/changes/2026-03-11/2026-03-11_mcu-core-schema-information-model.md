# 2026-03-11 MCU Core Schema Information Model

## 变更前问题

- `openpcb/agent/templates/architecture_fields/mcu_core.json` 直接把 `question_seed` 写进字段定义，schema 更像提问脚本，不像板卡信息模型。
- 模板加载器强依赖 `question_seed`，导致字段定义和交互文案耦合，难以把 schema 收敛为单片机核心板的设计事实库。
- `mcu_core` 模板是扁平 `fields` 列表，缺少按信息域分组的表达，设计语义不够清晰。

## 变更内容

- 将 `ArchitectureSchemaCollector` 的运行时字段从 `question_seed` 重构为 `prompt_hint`，并保留对旧模板 `question_seed` 的兼容读取。
- 为模板加载器增加 `field_groups` 支持，允许 schema 以信息域分组定义字段，并在加载时扁平化为采集流程可消费的 `field_map`。
- 将 `openpcb/agent/templates/architecture_fields/mcu_core.json` 升级为 `v2`，改成以 `板卡定位 / 主控选型 / 供电与接口 / 实现约束` 分组的 MCU 核心板信息模型。
- 提问文案改为由运行时基于 `label + description` 自动派生，不再要求在 schema 中维护 `question_seed`。
- 同步更新问句生成、CLI 交互与相关测试。

## 影响范围

- `openpcb/agent/architecture_schema_collector.py`
- `openpcb/agent/schema_question_generator.py`
- `openpcb/agent/prompts/schema_question_user_template.txt`
- `openpcb/cli/commands/chat.py`
- `openpcb/agent/templates/architecture_fields/mcu_core.json`
- `tests/agent/test_architecture_schema_collector.py`
- `tests/agent/test_schema_question_generator.py`
- `tests/cli/test_chat.py`

## 验证结果

- 已通过：
  - `pytest tests/agent/test_architecture_schema_collector.py tests/agent/test_schema_question_generator.py tests/cli/test_architecture_schema_collector_flow.py tests/cli/test_chat.py`

## 下一步建议

1. 将 `generic.json` 和 `power.json` 迁移到同样的 `field_groups + description` 结构，统一 schema 设计语言。
2. 为字段增加更强的类型信息，例如 `value_type`、`unit`、`multi_select`，继续弱化“问答脚本”色彩。
3. 后续如果要支持更多板型，优先复用这套信息模型风格，而不是继续追加 `question_seed` 类字段。
