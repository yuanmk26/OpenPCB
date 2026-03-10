# 2026-03-09_add-deepseek-provider

## 变更前问题

- 模型 provider 仅支持 `openai`，无法直接切换到 DeepSeek API。
- README 未给出 DeepSeek 的最小可运行配置示例。

## 变更内容

- 扩展 provider 支持：
  - `openpcb/config/settings.py` 支持 `openai` / `deepseek`
  - 增加 provider 默认值逻辑：
    - `openai` 默认 `model=gpt-4o-mini`、`base_url=https://api.openai.com/v1/chat/completions`
    - `deepseek` 默认 `model=deepseek-chat`、`base_url=https://api.deepseek.com/chat/completions`
- 更新 LLM client 工厂：
  - `openpcb/agent/llm/factory.py` 支持 `deepseek`（复用 OpenAI-compatible client）
- 更新配置示例：
  - `openpcb/config/example.config.toml` 增加 DeepSeek 示例块
- 更新任务文档：
  - `TODO_LIST.md` 中 G2 改为 OpenAI-Compatible（OpenAI/DeepSeek）
- 更新 README：
  - 新增 DeepSeek 快速配置与命令示例

## 影响范围

- 涉及文件：
  - `openpcb/config/settings.py`
  - `openpcb/agent/llm/factory.py`
  - `openpcb/config/example.config.toml`
  - `README.md`
  - `TODO_LIST.md`

## 验证结果

- 新增测试：
  - `tests/agent/test_config_loader.py::test_load_deepseek_defaults`
- 全量测试通过（见本次执行记录）。

## 下一步建议

1. 若后续引入 DeepSeek 专有参数（如 reasoning 选项），再扩展 `LLMRequest`。
2. 可补一条 e2e（mock server）验证 `--provider deepseek` 的请求 payload。

