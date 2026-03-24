# 2026-03-24 原理图预览 V1：TypeScript 几何模型与 SVG Viewer

## 变更前问题
- `SchematicPreview` 仍是静态占位卡片，无法承载原理图预览。
- 前端没有原理图几何模型、符号库引用、scene adapter 和 viewer 状态类型。
- 原理图预览尚未接真实后端，缺少可用于先行验证渲染链路的 mock 数据。

## 变更内容
- 新增 TypeScript 原理图类型定义，覆盖 `SchematicGeometry`、符号库、页面、实例、连线、标签、结点、标记和 `SchematicScene`。
- 新增 mock 几何数据和 `geometry -> scene` adapter，支持 symbol 引用展开、旋转/镜像变换、缺失符号降级标记。
- 将 `SchematicPreview` 升级为只读 SVG viewer，支持多页切换、缩放、重置、fit-to-page 和拖动平移。
- 为原理图 viewer 补充独立样式，保持现有深色工作台视觉语言。

## 影响范围
- `src/gui/ui/components/placeholders/SchematicPreview.tsx`
- `src/gui/ui/lib/mockSchematicGeometry.ts`
- `src/gui/ui/lib/schematicPreview.ts`
- `src/gui/ui/lib/schematicScene.ts`
- `src/gui/ui/types/schematic.ts`
- `src/gui/ui/styles/layout.css`

## 验证结果
- 计划执行 `npm run build` 验证 TypeScript 编译与前端打包链路。
- viewer 预期可直接渲染 mock 几何数据，并展示多页原理图只读预览。

## 下一步建议
- 将 `loadSchematicGeometry()` 从 mock 数据切换到 Tauri bridge 返回的真实 JSON payload。
- 为 adapter 和 viewer 引入前端自动化测试，覆盖旋转/镜像、分页和缺失 symbol 场景。
- 后续如需后端产出几何模型，再补 Python 侧等价 JSON 契约即可。
