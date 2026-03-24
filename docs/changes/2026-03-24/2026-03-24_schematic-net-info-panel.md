# 原理图网络名称点击详情

## 变更前问题
- 原理图预览中只有器件支持点击查看详情，网络名称标签无法交互。
- 右侧栏仅适配器件详情语义，无法统一承载器件和网络两类选中信息。

## 变更内容
- 将原理图选中状态扩展为统一的选中项类型，支持器件和网络两种详情。
- 为网络名称标签增加点击命中区域、选中高亮和右侧详情联动。
- 右侧栏调整为 `Selection Info`，可根据当前选中项展示器件或网络基础信息。
- 网络详情展示网络名、Net ID、样式类型、所在页、同页标签数量，以及缺失定义提示。

## 影响范围
- `src/gui/ui/types/ui.ts`
- `src/gui/ui/App.tsx`
- `src/gui/ui/components/workspace/Workspace.tsx`
- `src/gui/ui/components/shell/RightPanel.tsx`
- `src/gui/ui/components/placeholders/SchematicComponentInfoPanel.tsx`
- `src/gui/ui/components/placeholders/SchematicPreview.tsx`
- `src/gui/ui/styles/layout.css`

## 验证结果
- 已执行前端构建验证，确保 TypeScript 类型检查和 Vite 打包通过。
- 已检查交互实现覆盖器件点击、网络标签点击、空白区域取消选中，以及切换非原理图视图后的右栏恢复行为。

## 下一步建议
- 后续可扩展为点击导线段直接查看网络详情，并支持整网高亮。
- 若引入真实工程数据，可继续补充连接器件列表、跨页网络信息和网络约束详情。
