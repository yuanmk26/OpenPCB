# AGENTS.md

## Scope

These instructions apply to the whole repository.

## Mandatory Maintenance Rules

1. If any file is modified in a task, a change record must be added under `docs/changes/<YYYY-MM-DD>/`.
2. The change record file name must be `YYYY-MM-DD_<kebab-topic>.md`.
3. Each change record must include five sections:
   - 变更前问题
   - 变更内容
   - 影响范围
   - 验证结果
   - 下一步建议
4. If there is no code/file change, do not need to add changlog to `docs/changes`.

## Git Submission Rules

1. After create or modify any files, run `git add` + `git commit` + `git push` by default.
2. If push fails, keep the error output and report the reason clearly.
3. If the user explicitly requests not to commit/push, follow the user request as an exception.

## Notes

- Keep documentation statements aligned with current repository facts.
- Do not describe unimplemented capability as implemented.
