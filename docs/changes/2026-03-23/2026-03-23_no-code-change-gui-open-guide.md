# 2026-03-23_no-code-change-gui-open-guide

## 变更前问题
用户询问当前如何打开 OpenPCB 的 GUI 界面，缺少面向当前仓库结构的直接启动指令。

## 变更内容
- 未修改任何源代码或配置文件。
- 基于 `docs/gui/README.md` 与 `src/gui/package.json` 核对 GUI 启动命令。
- 给出可在 PowerShell 直接执行的 GUI 启动步骤（标记为 `no-code-change`）。

## 影响范围
- 文档记录新增：`docs/changes/2026-03-23/2026-03-23_no-code-change-gui-open-guide.md`
- 不影响 `src/openpcb` 与 `src/gui` 运行行为。

## 验证结果
- 已确认 GUI 子项目位于 `src/gui`。
- 已确认 `package.json` 存在 `tauri` 脚本，可通过 `npm run tauri dev` 启动开发 GUI。

## 下一步建议
1. 在项目根目录执行 `cd src/gui` 后运行 `npm.cmd install` 与 `npm.cmd run tauri dev`。
2. 若首次运行缺少 Rust/Tauri 依赖，按报错补齐后重试。
3. 后续可在 `docs/gui/README.md` 增补“常见启动故障”小节。
