## 变更前问题

GitHub Actions 在执行 `python -m pytest` 时于测试收集阶段失败。`tests/unit/test_settings.py` 导入 `openpcb.config.settings` 后，运行环境缺少 `pydantic_settings` 模块，导致 `ModuleNotFoundError`。

此外，本地测试环境中若存在通用环境变量 `DEBUG`，`Settings()` 也会被外部环境污染，导致 `test_settings.py` 出现与 CI 不一致的失败。

## 变更内容

在 `pyproject.toml` 的项目运行时依赖中补充 `pydantic-settings>=2.2,<3.0`，使 `pip install -e ".[dev]"` 安装出的 CI 环境包含 `Settings` 所需依赖。

同时调整 `tests/unit/test_settings.py`，在构造 `Settings` 时显式禁用 `.env` 文件读取，并临时移除外部 `DEBUG` 环境变量，确保测试只验证代码默认行为与显式传参行为。

## 影响范围

影响项目安装与 CI 依赖解析流程。`openpcb.config.settings` 及所有导入该模块的代码路径在新环境下可正常加载。

影响 `tests/unit/test_settings.py` 的执行稳定性，使本地环境与 CI 的测试结果更一致。

## 验证结果

已执行 `python -m pytest`，37 个测试全部通过。

## 下一步建议

后续新增运行时代码依赖时，建议同步检查 `pyproject.toml` 是否已声明，避免仅在本地已安装环境中可运行、但在 CI 中失败的情况。

如果后续继续扩展 `Settings` 的环境变量能力，建议考虑统一引入明确前缀，减少与系统级通用变量发生冲突的概率。
