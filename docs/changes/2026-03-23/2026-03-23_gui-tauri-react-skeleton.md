# 2026-03-23_gui-tauri-react-skeleton

## 变更前问题
- 仓库当前仅有 Python 主工程，缺少可运行的桌面 GUI 子工程。
- 尚未建立 Tauri + React + TypeScript + Vite 的基础工作台骨架。
- 尚未提供 GUI 架构文档与后续接入路线说明。

## 变更内容
- 新增 `src/gui/` 子工程，完成 Tauri v2 + React + TypeScript + Vite 最小脚手架。
- 前端源码固定在 `src/gui/ui/`，未使用 `src/gui/src/` 嵌套目录。
- 新增三栏工作台布局与占位组件：
  - Header: OpenPCB / MVP GUI Skeleton
  - Sidebar: Project / Files / Steps
  - Workspace: Requirement Panel / Chat Panel / Schematic Preview / Layout Preview
  - Right Panel: Planner Status / Tool Logs
- 新增未来扩展入口：
  - `src/gui/ui/lib/tauri.ts`
  - `src/gui/ui/types/ui.ts`
- 新增 GUI 文档：
  - `docs/gui/README.md`
  - `docs/gui/architecture.md`
  - `docs/gui/roadmap.md`

## 影响范围
- 新增目录：`src/gui/`（独立 GUI 子模块）
- 新增目录：`docs/gui/`（GUI 维护文档）
- 未修改 `src/openpcb/` 现有 Python 工程结构与运行逻辑。
- 新增依赖范围仅限 GUI 子工程的 Node/Tauri 依赖。

## 验证结果
- 结构验证：已创建所需目录分层与组件文件，满足 `src/gui/ui/` 约束。
- 命令验证：
  - `npm.cmd install`（在 `src/gui/` 执行）
  - `npm.cmd run build`（在 `src/gui/` 执行）
  - `npm.cmd run tauri dev`（在 `src/gui/` 执行）
- 已知限制：
  - 当前环境缺少 `rustc/cargo`，`tauri dev` 运行会受阻，需先安装 Rust toolchain。

## 下一步建议
1. 安装 Rust toolchain（含 `rustc` 与 `cargo`）并补齐 Tauri 平台依赖，完成桌面窗口本机验证。
2. 在 `ui/lib/tauri.ts` 中引入首个 typed command（如 `get_app_status`）并接入 `PlannerStatus`。
3. 为 `ToolLogs` 增加事件订阅链路，验证前端实时日志渲染流程。
