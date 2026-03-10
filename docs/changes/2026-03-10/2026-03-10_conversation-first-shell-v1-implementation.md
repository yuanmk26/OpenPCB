# 2026-03-10 conversation-first shell v1 实现落地

## 变更前问题
- `openpcb` 无参数默认仅显示帮助，不符合 conversation-first shell 目标。
- chat 普通文本会自动路由任务，缺少“纯聊天通道”。
- DeepSeek 接入对根地址兼容不足，且密钥读取缺少 `DEEPSEEK_API_KEY` 优先策略。

## 变更内容
- 默认入口改造：
  - `openpcb` 无参数直接进入交互式 chat shell。
  - `openpcb --help` 仍保持帮助输出。
- chat 行为改造：
  - 新增 `ChatAgent`，普通文本走 LLM 聊天回复。
  - 任务仅由 slash 命令触发，新增 `/plan <requirement>`、补齐 `/clear`。
- 配置与 LLM 客户端改造：
  - 默认 provider 改为 `deepseek`。
  - `provider=deepseek` 时 API key 按 `DEEPSEEK_API_KEY -> OPENPCB_API_KEY` 读取。
  - OpenAI-compatible 客户端支持 DeepSeek 根地址自动补全 `/chat/completions`。

## 影响范围
- 受影响模块：
  - CLI：`main`、`chat`、`presenter`
  - Agent：`chat_agent`、`session`、`llm/openai_client`、`llm/types`
  - Config：`settings`、`loader`
  - Tests：agent + cli 相关测试
- 兼容性说明：
  - `openpcb chat` 仍可使用；
  - 旧的文本自动任务路由语义不再作为默认行为。

## 验证结果
- 执行命令：
  - `pytest tests/agent/test_config_loader.py tests/agent/test_openai_client.py tests/agent/test_session.py tests/cli/test_help.py tests/cli/test_chat.py`
- 结果摘要：
  - 18 passed

## 下一步建议
1. 在 v2 引入 TaskRouter，将聊天意图升级为任务执行的策略做成可配置能力。
2. 增加 chat 级别的 system prompt 配置项，支持项目级定制。

