# 2026-03-09_fix-editable-install-package-discovery

## 变更前问题

- 执行 `pip install -e .` 报错：`Multiple top-level packages discovered in a flat-layout: ['demo', 'openpcb']`。
- `project.license` 使用 TOML table 形式触发 setuptools 弃用警告。

## 变更内容

- 更新 `pyproject.toml`：
  - 将 `project.license` 从 `{ text = "Apache-2.0" }` 改为 `"Apache-2.0"`。
  - 新增 `tool.setuptools.packages.find`，显式限制只打包 `openpcb*`，并排除 `demo/examples/tests/docs/scripts`。

## 影响范围

- 受影响文件：`pyproject.toml`
- 影响行为：editable install 的包发现策略从自动发现改为显式发现，避免顶层非包目录误打包。

## 验证结果

- 预期：`pip install -e .` 不再出现多顶层包发现错误。

## 下一步建议

1. 若后续引入新顶层包目录，记得同步更新 `tool.setuptools.packages.find`。
2. 统一在 README 或开发文档中固定安装命令（建议 `python -m pip install -e .`）。

