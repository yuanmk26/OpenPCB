# 2026-03-09_llm-integration-openai

## 变更前问题

- `plan` 主要依赖规则 mock，未接入真实模型调用。
- 缺少 API key 配置层与 provider 抽象，无法稳定对接外部模型。
- `TODO_LIST` 未覆盖模型接入任务块，后续排期缺失。

## 变更内容

- 新增配置与密钥管理：
  - `openpcb/config/settings.py`
  - `openpcb/config/loader.py`
  - `openpcb/config/example.config.toml`
  - `.gitignore` 新增 `openpcb.config.toml`
- 新增 LLM 抽象层（OpenAI 单提供商）：
  - `openpcb/agent/llm/types.py`
  - `openpcb/agent/llm/base.py`
  - `openpcb/agent/llm/openai_client.py`
  - `openpcb/agent/llm/factory.py`
- planner 重构：
  - 默认走 LLM 规划
  - 保留 `use_mock_planner` 开关用于测试/降级
  - 增加 JSON 提取与严格解析
- runtime 与 CLI 接入：
  - `runtime._planner_tool` 改为加载配置并调用 LLM planner
  - `plan` 增加 `--provider --model --config --use-mock-planner`
  - trace 增加 `llm_meta`（provider/model/token/latency）
- 文档更新：
  - `TODO_LIST.md` 新增 `Milestone G: Model Integration`
  - `README.md` 新增“模型接入配置（OpenAI）”

## 影响范围

- 受影响模块：
  - `openpcb/config/*`
  - `openpcb/agent/llm/*`
  - `openpcb/agent/planner.py`
  - `openpcb/agent/runtime.py`
  - `openpcb/cli/commands/plan.py`
- 行为变化：
  - `plan` 默认需要可用 API key（未配置时直接报错）。
  - 通过 `--use-mock-planner` 可强制走 mock。

## 验证结果

- 新增测试：
  - `tests/agent/test_config_loader.py`
  - `tests/agent/test_openai_client.py`
  - `tests/agent/test_planner_json_parse.py`
- 更新测试：
  - `tests/cli/test_plan_build.py`
  - `tests/cli/test_check_edit.py`
- 验证重点：
  - 无 key 失败路径
  - mock 模式可跑通 plan/build/check/edit
  - OpenAI client 响应与错误映射

## 下一步建议

1. 增加 provider 指标上报（成功率、响应时延分布）到 trace/report。
2. 后续扩展 OpenAI 兼容多 base_url（如代理网关）时补充集成测试。

