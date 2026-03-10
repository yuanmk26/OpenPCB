# 2026-03-09_readme-reinstall-commands

## 变更前问题

- 用户确认 `python -m pip uninstall -y openpcb` + 重装命令有效，但 README 未明确提供这套“彻底切换版本”步骤。
- 遇到 `No such option: --project-name` 时，用户不容易第一时间定位为旧包污染。

## 变更内容

- 在 `README.md` 中新增“方式 3：彻底切换到当前版本”小节。
- 小节包含：
  - 卸载旧版本（执行两次）命令
  - 回到仓库根目录执行 `pip install -e .`
  - 使用 `pip show` / `import openpcb` / `plan --help` 三步验证
  - 推荐固定使用 `d:\anaconda3\python.exe -m openpcb ...`

## 影响范围

- 受影响文件：`README.md`
- 仅文档更新，不涉及代码逻辑。

## 验证结果

- README 已包含可直接复制执行的“重装与切换”命令块。
- 新小节覆盖了用户本次反馈的有效命令方案。

## 下一步建议

1. 在 README 顶部加“环境排查”目录锚点，便于快速跳转。
2. 后续若引入虚拟环境，补充 `venv/conda` 场景的并行说明。

