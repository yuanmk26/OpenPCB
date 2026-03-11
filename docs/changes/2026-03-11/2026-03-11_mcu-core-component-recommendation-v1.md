# 2026-03-11 MCU Core Component Recommendation V1

## 变更前问题

- 现有架构交互只能补齐字段，无法在讨论主控、电源、收发器等模块时基于参数约束推荐具体器件。
- 用户如果只描述“大概参数”而没有明确型号，系统无法继续推进到可执行的器件选型建议。
- 即使交互中形成了器件选择意向，也没有落到 `project.metadata`，后续 planner 无法直接消费。

## 变更内容

- 新增 `openpcb/agent/component_recommender.py`，提供本地 catalog 加载、模块类型识别、参数问题集和规则排序推荐能力。
- 新增本地器件库 `openpcb/agent/templates/component_catalog/`，首版包含 `mcu.json`、`power.json`、`transceiver.json`。
- 在 `chat` 架构交互中新增器件推荐子流程：
  - 仅对 `mcu_core` 生效
  - 在板级 P0 信息补齐后自动识别模块讨论
  - 逐项追问最小参数集
  - 输出最多 3 个候选并允许用户确认
  - 直接输入明确型号时跳过推荐，直接记录
- 扩展 session 和 runtime，将 `component_recommendations` 写入 `project.metadata`。
- 增加推荐服务单元测试与 CLI 集成测试。

## 影响范围

- `openpcb/agent/component_recommender.py`
- `openpcb/agent/templates/component_catalog/mcu.json`
- `openpcb/agent/templates/component_catalog/power.json`
- `openpcb/agent/templates/component_catalog/transceiver.json`
- `openpcb/agent/session.py`
- `openpcb/agent/runtime.py`
- `openpcb/cli/commands/chat.py`
- `tests/agent/test_component_recommender.py`
- `tests/cli/test_chat.py`

## 验证结果

- 已通过：
  - `pytest tests/agent/test_architecture_schema_collector.py tests/agent/test_schema_question_generator.py tests/agent/test_component_recommender.py tests/cli/test_architecture_schema_collector_flow.py tests/cli/test_chat.py`

## 下一步建议

1. 将推荐结果与 planner 的模块生成逻辑建立更明确的映射，减少后续规划阶段重复判断。
2. 为器件库增加更结构化的数值字段，例如电流、输入范围、速率上限，降低字符串匹配带来的模糊性。
3. 后续再考虑引入外部器件数据源，但应保留本地 catalog 作为稳定兜底。
