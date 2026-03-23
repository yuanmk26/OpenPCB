# 2026-03-23_no-code-change-fix-tauri-cargo-missing

## 变更前问题
在 `src/gui` 执行 `npm run tauri dev` 时，报错 `program not found`，无法运行 `cargo metadata`。

## 变更内容
- 未修改任何源码或配置文件（no-code-change）。
- 在当前环境检查 `cargo --version`、`rustup --version`、`where cargo`，均确认不可用。
- 明确问题根因是本机缺少 Rust/Cargo 工具链或 PATH 未生效，而非仓库代码问题。

## 影响范围
- 新增文档记录：`docs/changes/2026-03-23/2026-03-23_no-code-change-fix-tauri-cargo-missing.md`。
- 不影响 `src/gui` 与 `src/openpcb` 任何运行逻辑。

## 验证结果
- `cargo --version`：命令不存在。
- `rustup --version`：命令不存在。
- `where cargo`：未找到路径。
- 结论：安装并正确配置 Rust 工具链后，Tauri 命令可继续执行。

## 下一步建议
1. 安装 Rust（包含 cargo）并重启终端。
2. 运行 `cargo --version` 与 `rustup --version` 验证。
3. 回到 `src/gui` 执行 `npm.cmd run tauri dev`。
