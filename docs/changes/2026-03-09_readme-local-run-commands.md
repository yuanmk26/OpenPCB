# 2026-03-09_readme-local-run-commands

## 变更前问题

- 用户在本地可能命中旧 `openpcb.exe`，导致与仓库源码行为不一致。
- README 缺少一段“如何稳定运行当前修改版本”的明确命令指引。

## 变更内容

- 在 `README.md` 追加“使用本地最新版本（推荐）”小节。
- 小节包含三部分：
  - 方式 1：`python -m openpcb` 直接运行源码入口
  - 方式 2：`scripts/use-local-openpcb.ps1` 脚本运行
  - 验证方式：打印 `python/openpcb.__file__/openpcb.__version__`

## 影响范围

- 受影响文件：`README.md`
- 本次仅文档更新，不涉及代码逻辑调整。

## 验证结果

- README 已包含可直接复制执行的命令块（PowerShell）。
- 命令内容与当前仓库新增入口（`openpcb/__main__.py`、`scripts/use-local-openpcb.ps1`）一致。

## 下一步建议

1. 后续在 README 顶部目录增加“本地开发运行”跳转锚点，提升可发现性。
2. 补充一段“常见环境冲突排查”（`where openpcb` / `where python`）。

