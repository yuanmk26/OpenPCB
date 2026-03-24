# 2026-03-24 原理图预览可见性修复

## 变更前问题
- 原理图预览首屏按整页缩放，器件内容区域过小，看起来像白板。
- mock 符号图元仍带浅色描边，在浅色纸面上几乎不可见。
- 缩放后线条继续变细，进一步削弱了器件主体的可见性。

## 变更内容
- 为 `SchematicPageScene` 增加 `contentBounds`，并在 scene adapter 中汇总实例、导线、标签、结点等内容边界。
- 将 viewer 的初始视口和 `Fit` 行为改为按内容区域聚焦，不再默认整页 fit。
- 将 mock 符号图元描边统一改为深色，并在 viewer 中增加浅色描边归一化兜底。
- 为导线、器件图元、结点和标记增加非缩放描边，保证缩小时仍可见。

## 影响范围
- `src/gui/ui/types/schematic.ts`
- `src/gui/ui/lib/mockSchematicGeometry.ts`
- `src/gui/ui/lib/schematicScene.ts`
- `src/gui/ui/components/placeholders/SchematicPreview.tsx`

## 验证结果
- 计划执行 `node node_modules\\typescript\\bin\\tsc --noEmit` 与 `npm.cmd run build` 验证类型和打包。
- 预期第一页和第二页打开后均能直接看到器件主体，不再是仅有白纸和少量线网。

## 下一步建议
- 为 `Fit Content` 和 `Fit Page` 提供两个独立按钮，避免后续调试页面框时互相干扰。
- 后续如果接入真实几何模型，建议保留 viewer 颜色归一化兜底，避免旧 symbol 样式再次导致不可见。
