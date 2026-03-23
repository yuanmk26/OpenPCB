# GUI 三栏工作台布局重构

## 变更前问题
- 现有 GUI 布局为左侧导航、中间四宫格、右侧状态日志，和目标使用场景不一致。
- 聊天区位于中间区域，不利于连续展示用户与 agent 的主交互流。
- 中间区域同时展示多个卡片，缺少用于在 Files / Schematic / Layout 间单选切换的统一入口。
- 右侧未聚焦需求与元件库等项目信息，信息组织方向偏执行日志。

## 变更内容
- 将 `App` 主体重排为三栏：左侧聊天列、中间工作区、右侧信息区。
- 新增 `ChatColumn`，将 `ChatPanel` 固定到左侧栏位。
- 重构 `Workspace`：
  - 新增 `WorkspaceView` 视图状态与顶部单选标签栏。
  - 支持 `Files / Schematic Preview / Layout Preview` 三视图互斥切换。
  - 新增 `FilesPanel` 占位组件作为文件视图首版容器。
- 重构右侧面板为项目信息聚合区：
  - `RequirementPanel`
  - `ComponentLibraryPanel`（新增）
  - `ProjectOverviewPanel`（新增）
- 更新 `layout.css`，实现三栏栅格比例、切换标签激活态、滚动区域与响应式堆叠（窄屏顺序为聊天 -> 中间 -> 信息）。
- 在 `ui/types/ui.ts` 中新增：
  - `WorkspaceView`
  - `InfoPanelSection`

## 影响范围
- 前端 GUI 壳层与布局样式（`src/gui/ui`）发生结构调整。
- 占位组件职责与页面位置变化，不涉及后端接口与 Tauri 命令协议变更。
- 旧 `Sidebar`、`PlannerStatus`、`ToolLogs` 组件未删除，但不再作为当前主布局渲染路径。

## 验证结果
- 在 `src/gui` 执行构建验证通过：
  - `npm.cmd run build`
  - 实际执行为 `tsc --noEmit && vite build`
- 构建产物正常生成，确认无 TypeScript 编译错误和 Vite 打包错误。

## 下一步建议
- 将 `FilesPanel` 升级为真实项目文件树与文件预览能力。
- 为聊天区补充消息列表、输入框、滚动锚定和多角色消息样式。
- 为右侧信息区补充需求数据绑定、元件库筛选与项目关键指标卡片。
