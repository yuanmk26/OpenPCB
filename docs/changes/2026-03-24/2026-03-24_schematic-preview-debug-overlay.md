# 2026-03-24 原理图预览诊断层

## 变更前问题
- 原理图预览异常时，仅靠肉眼难以判断是视口、纸张、内容边界还是器件图元出了问题。
- 运行时没有显式的调试网格、bounds 框和最小样本，定位渲染链路故障成本较高。

## 变更内容
- 在 `SchematicPreview` 中新增 `Debug` 开关，开启后额外渲染整屏调试网格、原点、`pageBounds`、`contentBounds` 和 `instance.bounds`。
- 新增最小诊断样本图元，绕过真实 symbol 数据，用于验证 SVG / viewport 本身是否工作正常。
- 在状态栏显示 `viewport.mode`、`scale`、`pan` 以及当前页边界数值，便于判断是否是视口算错。
- 为调试标签补充样式，提升运行时排查可读性。

## 影响范围
- `src/gui/ui/components/placeholders/SchematicPreview.tsx`
- `src/gui/ui/styles/layout.css`

## 验证结果
- 计划执行 `node node_modules\\typescript\\bin\\tsc --noEmit` 与 `npm.cmd run build` 验证类型与打包。
- debug 开启后应能直接看到网格、边界框和最小诊断样本。

## 下一步建议
- 基于 debug overlay 的实际显示结果，再决定是继续修视口、修 instance transform，还是修 symbol 图元展开。
- 若调试层正常而真实器件仍不可见，可进一步在 scene adapter 输出原始实例和图元数量统计。
