# 2026-03-23_no-code-change-rust-cargo-path-persist

## 变更前问题
用户已可通过临时方式 `$env:Path += ";$HOME\.cargo\bin"` 识别 `cargo`，说明 Rust 已安装但 PATH 未持久生效。

## 变更内容
- 未修改任何源码或配置文件（no-code-change）。
- 明确故障点为用户环境变量 PATH 缺少 `~/.cargo/bin` 的持久项。
- 给出 PowerShell 下用户级 PATH 持久写入与验证步骤。

## 影响范围
- 新增文档记录：`docs/changes/2026-03-23/2026-03-23_no-code-change-rust-cargo-path-persist.md`。
- 不影响仓库代码与运行逻辑。

## 验证结果
- 用户终端已验证：临时追加 PATH 后 `cargo --version` 正常输出 `1.94.0`。
- 结论：Rust 工具链可用，需完成 PATH 持久化后再正常启动 Tauri GUI。

## 下一步建议
1. 将 `$HOME\.cargo\bin` 写入用户级 PATH 并重开终端。
2. 验证 `cargo --version` 与 `rustup --version`。
3. 回到 `src/gui` 执行 `npm.cmd run tauri dev`。
