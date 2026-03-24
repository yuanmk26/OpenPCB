# 原理图器件点击详情面板

## 变更前问题
- 原理图预览中的器件无法被选中，用户点击器件后右侧栏目不会展示任何对应信息。
- 右侧栏始终固定显示项目级占位内容，无法随原理图交互切换到器件详情视图。

## 变更内容
- 在应用顶层新增工作区视图与当前选中原理图器件的共享状态。
- 为原理图预览增加器件点击命中区域、选中高亮和空白区域取消选中行为。
- 新增右侧器件详情卡，并在原理图视图下替换原有项目占位面板。
- 详情卡展示基础信息：RefDes、Value、器件名、Symbol ID、所在页，以及缺失符号提示。

## 影响范围
- `src/gui/ui/App.tsx`
- `src/gui/ui/components/workspace/Workspace.tsx`
- `src/gui/ui/components/placeholders/SchematicPreview.tsx`
- `src/gui/ui/components/shell/RightPanel.tsx`
- `src/gui/ui/components/placeholders/SchematicComponentInfoPanel.tsx`
- `src/gui/ui/types/ui.ts`
- `src/gui/ui/styles/layout.css`

## 验证结果
- 已执行前端构建验证，确认 TypeScript 类型检查与 Vite 打包通过。
- 已检查交互链路实现：原理图视图下支持选中器件、右栏展示详情、切出原理图视图后恢复原有右栏内容。

## 下一步建议
- 后续可扩展器件详情卡，增加引脚列表、位号坐标、封装映射或网络连接信息。
- 若后端原理图数据源接入完成，可将当前 mock 详情对象替换为真实工程数据。
