# 2026-03-11 Component Selection P0 Skip Gate

## 变更前问题

- 器件推荐虽然已经接入架构交互，但不会阻塞 `/yes -> plan`，因此器件选型并不真正属于 P0 门禁。
- 用户如果暂时不想决定某个器件，只能取消当前推荐流程，无法显式标记“跳过该器件选型”。
- 帮助信息里没有对应的跳过入口，交互语义不完整。

## 变更内容

- 将已触发的器件选型纳入 `P0` 规划门禁：若某个器件推荐流程已开始，但既未确认型号也未跳过，则 `/yes` 会被阻塞。
- 新增 `/skip` 命令，并支持在器件推荐过程中输入 `skip` / `跳过` 等文本，显式跳过当前器件选型。
- 跳过后会把该器件推荐记录写入 `component_recommendations`，并标记 `source = skipped`、`priority = P0`。
- 更新帮助信息，并增加对应 CLI 回归测试。

## 影响范围

- `openpcb/cli/commands/chat.py`
- `openpcb/cli/presenter.py`
- `tests/cli/test_chat.py`

## 验证结果

- 已通过：
  - `pytest tests/cli/test_chat.py tests/cli/test_help.py tests/agent/test_component_recommender.py`

## 下一步建议

1. 将器件门禁的阻塞提示从类别名提升为更用户友好的模块名。
2. 后续可把 `skipped` 原因做成结构化字段，而不是只记录状态。
3. 如需更严格的门禁，可以进一步区分“已讨论模块必须选型”与“仅被顺带提及模块可忽略”的判定规则。
