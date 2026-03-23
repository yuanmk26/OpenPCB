# 2026-03-23_no-code-change-rust-toolchain-missing-followup

## 变更前问题
用户在 PowerShell 中执行 `cargo --version` 与 `rustup --version` 均提示命令不存在，无法继续启动 Tauri GUI。

## 变更内容
- 未修改任何源代码或配置文件（no-code-change）。
- 根据用户终端输出确认 Rust 工具链未安装或 PATH 未生效。
- 提供安装 rustup/cargo、重启终端、验证命令、回到 GUI 启动的闭环操作建议。

## 影响范围
- 新增文档记录：`docs/changes/2026-03-23/2026-03-23_no-code-change-rust-toolchain-missing-followup.md`。
- 不影响项目源码和运行逻辑。

## 验证结果
- 用户输出显示：
  - `cargo` 命令不可识别
  - `rustup` 命令不可识别
- 结论：需先安装 Rust 工具链，再运行 `npm run tauri dev`。

## 下一步建议
1. 安装 rustup（会安装 cargo）并重启终端。
2. 运行 `rustup --version` 与 `cargo --version` 验证。
3. 回到 `src/gui` 重新执行 `npm.cmd run tauri dev`。
