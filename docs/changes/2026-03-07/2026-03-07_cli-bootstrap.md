# 2026-03-07_cli-bootstrap

## 变更前问题

- 仓库中 `openpcb/cli`、`openpcb/io`、`openpcb/agent` 主要文件基本为空，CLI 无法形成可执行链路。
- `pyproject.toml` 为空，`openpcb` 命令入口与依赖未配置，无法稳定安装与运行。
- `tests/` 下没有可用测试，最小功能没有自动化验收。

## 变更内容

- 完成了 Python 包与 CLI 基础可运行层：
  - 配置 `pyproject.toml`（项目元数据、依赖、`openpcb` 控制台脚本、pytest 配置）。
  - 新增 `openpcb/__init__.py` 并定义 `__version__`。
  - 实现 CLI 主入口：注册 `version/init/plan/generate/check/edit`，支持全局 `--verbose`。
- 实现了 `openpcb init` 最小闭环：
  - 支持 `openpcb init <project_name> [--dir]`。
  - 自动创建 `project.json`、`plan.md`、`output/`、`logs/`。
  - 补齐 `project_saver` 与 `project_loader` 的最小读写能力。
- 补齐错误体系：
  - 新增 `OpenPCBError`、`InputError`、`FileConflictError`、`SaveError`。
  - CLI 错误输出统一为可读信息，并返回非零退出码。
- 预埋 `plan` 命令骨架：
  - 接收自然语言参数。
  - 当前返回 `mock planner not implemented yet`（明确提示后续将进入 parser -> planner -> saver 流程）。
- `generate/check/edit` 当前为占位命令，返回“未实现”提示与非零退出码。

为什么这样做：
- 先完成可安装、可执行、可初始化项目的最小闭环（M0-M2），确保后续功能在稳定入口上迭代。
- 保留占位命令可避免接口频繁变动，降低后续接入真实能力时的重构成本。

## 影响范围

- 受影响命令：
  - `openpcb --help`
  - `openpcb version`
  - `openpcb init`
  - `openpcb plan`（骨架）
  - `openpcb generate/check/edit`（占位）
- 关键新增/修改文件（示例）：
  - `pyproject.toml`
  - `openpcb/cli/main.py`
  - `openpcb/cli/commands/init.py`
  - `openpcb/cli/commands/plan.py`
  - `openpcb/io/project_saver.py`
  - `openpcb/io/project_loader.py`
  - `openpcb/utils/errors.py`
  - `tests/cli/test_help.py`
  - `tests/cli/test_version.py`
  - `tests/cli/test_init.py`
- 兼容性说明：
  - 这是 v0.1 启动阶段变更，尚未实现完整的 schema/agent/generate/check/edit 业务逻辑。

## 验证结果

- 执行并通过：
  - `pytest -q` -> `3 passed`
  - `openpcb --help` -> 正常显示命令列表
  - `openpcb version` -> 输出 `0.1.0a0`
  - `openpcb init demo_board --dir <temp>` -> 成功创建项目目录与基础文件
- 已知限制：
  - `plan` 仅为骨架，未接入 mock planner 实现。
  - `generate/check/edit` 仍为占位逻辑。
  - 当前测试仅覆盖 help/version/init 的最小路径。

## 下一步建议

1. 进入 M3：实现 `plan` 的规则+mock 路径（parser -> planner -> saver）并补齐对应测试。
2. 在 `docs/changes/` 按本规范持续记录每次任务，保证后续改动可追溯。

