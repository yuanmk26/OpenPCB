# 2026-03-24 原理图渲染修正：切回 EDA 标准预览

## 变更前问题
- 原理图预览使用深色装饰化卡片视觉，整体更像仪表盘插画，不像正常原理图。
- viewer 没有渲染 pin name 和 pin number，器件只剩主体框和少量文字，读图信息不完整。
- 缺失 symbol 时只显示彩色 marker，没有标准占位器件表达。

## 变更内容
- 将原理图区改为纸面化 SVG 表达，去除渐变装饰、彩色胶囊标签和非 EDA 风格的主视觉。
- 为 `SymbolPin` 增加 `number` 字段，并在 scene adapter 中生成可直接渲染的 pin 文本布局信息。
- viewer 改为渲染 pin name、pin number、标准 net label、title block 和缺失 symbol 占位框。
- 保留缩放、平移、多页切换能力，同时让文字保持正常可读的原理图表达。

## 影响范围
- `src/gui/ui/types/schematic.ts`
- `src/gui/ui/lib/mockSchematicGeometry.ts`
- `src/gui/ui/lib/schematicScene.ts`
- `src/gui/ui/components/placeholders/SchematicPreview.tsx`
- `src/gui/ui/styles/layout.css`

## 验证结果
- 计划执行 `node node_modules\\typescript\\bin\\tsc --noEmit` 和 `npm.cmd run build` 验证类型与打包。
- viewer 预期应更接近 KiCad/Altium 风格的只读原理图预览。

## 下一步建议
- 为电源符号、地符号、no-connect 标记等标准原理图元素补专门图元。
- 后续可加入 hover 高亮 net / pin，但保持纸面风格不回退为装饰化 UI。
