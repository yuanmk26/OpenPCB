# 2026-03-24 Tauri Dev 图标缺失修复

## 变更前问题
- 在 Windows 上执行 `npm run tauri dev` 时，`tauri-build` 需要生成资源文件。
- `src/gui/src-tauri/icons/icon.ico` 缺失，导致构建在 `build.rs` 阶段失败。

## 变更内容
- 在 `src/gui/src-tauri/tauri.conf.json` 中显式配置 `bundle.icon` 指向 `icons/icon.ico`。
- 新增一个最小可用的占位图标文件 `src/gui/src-tauri/icons/icon.ico`，用于满足 Tauri Windows 资源生成要求。

## 影响范围
- `src/gui/src-tauri/tauri.conf.json`
- `src/gui/src-tauri/icons/icon.ico`

## 验证结果
- 预期 `npm run tauri dev` 不再因为缺失 `icons/icon.ico` 失败。
- 后续如仍有 Rust/Tauri 侧错误，应进入下一层配置或代码排查，而不是资源缺失。

## 下一步建议
- 用正式品牌图标替换当前占位 `icon.ico`。
- 如果后续需要打包安装程序，再补齐 `.png`、`.icns` 等平台资源，避免各平台 bundle 阶段继续缺图。
