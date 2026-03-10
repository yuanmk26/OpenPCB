# 2026-03-08_local-openpcb-runner

## 变更前问题

- 终端中的 `openpcb` 可能指向旧安装版本，导致命令行为与仓库代码不一致。
- 已修改源码后，用户仍可能看到 `mock planner not implemented yet` 等旧提示。

## 变更内容

- 新增模块入口：`openpcb/__main__.py`
  - 支持 `python -m openpcb ...` 直接运行当前源码对应的 CLI。
- 新增本地运行脚本：`scripts/use-local-openpcb.ps1`
  - 自动执行 `pip install -e .`
  - 打印当前 Python 与 `openpcb` 实际加载路径/版本
  - 使用 `python -m openpcb` 执行命令，规避旧 `openpcb.exe` 干扰

## 影响范围

- 受影响文件：
  - `openpcb/__main__.py`
  - `scripts/use-local-openpcb.ps1`
- 不影响业务逻辑，仅影响“如何确保运行的是最新源码”。

## 验证结果

- 通过 `python -m openpcb version` 可直接验证当前源码版本。
- 通过 `scripts/use-local-openpcb.ps1 plan ...` 可强制走本地源码入口。

## 下一步建议

1. 日常开发时优先使用 `python -m openpcb ...` 或该脚本。
2. 发布前再验证 `openpcb.exe` 路径和版本，避免环境残留影响验收。

