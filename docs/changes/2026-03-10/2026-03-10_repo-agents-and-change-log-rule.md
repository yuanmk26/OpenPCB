# 2026-03-10 仓库级维护规则补充（AGENTS）

## 1. 变更前问题

- 维护规则主要分散在 `docs/README.md` 与 `docs/architecture/README.md`，不属于仓库根级统一指令。
- 对“每次修改都要补 `docs/changes` 文档”的约束缺少统一、直接的仓库入口说明。
- 导致执行上依赖人工记忆，近期出现过未自动执行提交流程的情况。

## 2. 变更内容

- 在仓库根新增 `AGENTS.md`，定义为全仓库适用规则。
- 新增并明确两类强制规则：
  - 若任务有文件修改，必须在 `docs/changes/<YYYY-MM-DD>/` 新增当日变更文档。
  - 每次任务完成后默认执行 `git add` + `git commit` + `git push`。
- 同时写入异常处理约束：
  - push 失败要保留报错并说明原因。
  - 用户明确要求不提交/不推送时按用户要求豁免。

## 3. 影响范围

- 新增文件：`AGENTS.md`
- 新增文件：`docs/changes/2026-03-10/2026-03-10_repo-agents-and-change-log-rule.md`
- 该变更为流程治理层，不影响运行时代码与 CLI 功能。

## 4. 验证结果

- 已确认根目录存在 `AGENTS.md`，内容包含“修改必写 changes 文档”和“默认 add/commit/push”规则。
- 已补充当日 changes 文档，满足“有修改必记录”约束。
- 当前工作区仅包含本次规则文档新增，符合预期。

## 5. 下一步建议

1. 后续所有任务统一以 `AGENTS.md` 为首要维护规则入口执行。
2. 如需更强约束，可后续增加 pre-commit 或 CI 校验（例如检测当日改动是否伴随 `docs/changes/<date>/` 记录）。
