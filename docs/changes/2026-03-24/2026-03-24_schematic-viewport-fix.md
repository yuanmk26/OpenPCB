# 2026-03-24 原理图预览视口修正

## 变更前问题
- 原理图预览在内容聚焦时，经常出现纸张偏到一角的情况。
- 首屏会出现左上大片白纸、右下大片工作区背景，器件区域不在主要视野范围内。
- 现有单层 `translate + scale` 视口变换容易让平移量随缩放被放大。

## 变更内容
- 为 `ViewportState` 增加 `mode`，明确区分 `content` 与 `page` 两种视口模式。
- 新增 `fitViewportToContent` 和 `fitViewportToPage`，分离内容聚焦与整页观察的计算逻辑。
- 将 SVG 视口变换拆为两层：外层平移、内层缩放，避免平移量被缩放二次放大。
- viewer 工具栏增加 `Fit Content` 和 `Fit Page`，切页后默认回到内容聚焦模式。

## 影响范围
- `src/gui/ui/types/schematic.ts`
- `src/gui/ui/lib/schematicScene.ts`
- `src/gui/ui/components/placeholders/SchematicPreview.tsx`

## 验证结果
- `node node_modules\\typescript\\bin\\tsc --noEmit` 通过。
- `npm.cmd run build` 通过。
- 预期首屏纸张与器件区域会保持在主要视区，不再偏到角落。

## 下一步建议
- 后续可在状态栏显示当前视口模式，便于调试 `Fit Content` / `Fit Page` 的行为。
- 如果后面接入真实几何模型，可增加基于内容边界的最小/最大缩放限制，避免极端页面尺寸影响首屏体验。
