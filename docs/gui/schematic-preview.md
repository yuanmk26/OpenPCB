# Schematic Preview

## Purpose
`SchematicPreview` is the current GUI-side schematic rendering demo for OpenPCB.

Its role today is to validate:
- scene unit and page-fit behavior
- symbol and wire rendering pipeline
- viewport interaction behavior inside the workbench
- GUI-side data contracts for future real schematic sources

It is not yet a full schematic editor or a production renderer.

## Current Entry Points
- Preview component: `src/gui/ui/components/placeholders/SchematicPreview.tsx`
- Mock geometry source: `src/gui/ui/lib/mockSchematicGeometry.ts`
- Scene builder and viewport fit: `src/gui/ui/lib/schematicScene.ts`
- Shared metrics and unit system: `src/gui/ui/lib/schematicMetrics.ts`
- Type contracts: `src/gui/ui/types/schematic.ts`

## Current Data Flow
1. `SchematicPreview.tsx` loads preview geometry through `loadSchematicGeometry()`.
2. Geometry is currently backed by TypeScript mock data.
3. `buildSchematicScene()` resolves symbol instances into page-scene objects.
4. The component selects the active page and computes viewport state.
5. The page is rendered as SVG layers inside the workbench panel.

## Rendering Architecture
The current rendering stack is split into four layers.

### 1. Geometry Layer
`SchematicGeometry` describes:
- symbol library
- pages
- instances
- wires
- net labels
- junctions
- markers
- net metadata

This is the raw input contract before render-time transforms.

### 2. Scene Resolution Layer
`buildSchematicScene()` converts geometry pages into `SchematicPageScene`.

This stage is responsible for:
- symbol lookup
- instance transform resolution
- pin anchor resolution
- bounds generation
- content bounds aggregation
- fallback placeholder generation for missing symbols

If a symbol is missing, the renderer does not fail hard. It creates a placeholder symbol and pushes an error marker into the page scene.

### 3. Viewport Layer
Viewport state is tracked as:
- `pageId`
- `scale`
- `pan`
- `mode`

Supported viewport modes:
- `page`: fit full page into the panel
- `content`: fit content bounds while keeping the page inside the viewport
- `manual`: user-controlled pan/zoom state

Current viewport helpers:
- `fitViewportToPage()`
- `fitViewportToContent()`
- component-side pan clamping

### 4. SVG Presentation Layer
`SchematicPreview.tsx` renders SVG in this order:
- stage background
- optional debug screen grid
- page paper
- page grid
- locator circle
- page frame and title block
- wires
- junctions
- symbols
- labels
- markers
- optional debug overlays

This means the preview is a retained SVG scene, not a canvas-based raster renderer.

## Supported Rendered Content
The current preview supports these visible schematic elements.

### Page-Level
- page paper rectangle
- inner page grid
- page frame
- title block
- page title and sheet metadata

### Symbols and Instances
- symbol placement by page position
- rotation: `0`, `90`, `180`, `270`
- mirror flag in the scene transform path
- refdes/value text
- missing-symbol placeholder rendering

### Primitive Types
Supported symbol graphic primitives:
- `rect`
- `line`
- `circle`
- `polyline`
- `text`
- `pin_stub`

### Connectivity and Annotations
- wires with style variants: `signal`, `power`, `ground`, `clock`
- junction dots
- net labels
- page markers with warning or error intent
- generated marker for missing symbols

### Interaction
- page switching
- `Fit Content`
- `Fit Page`
- button zoom in/out
- mouse wheel zoom
- drag pan
- debug toggle

## Current Mock Coverage
The current mock library is intentionally small and demo-oriented.

Included symbol definitions:
- `usb-c-input`
- `ldo`
- `mcu`
- `debugger`

Included page examples:
- `page-power`
- `page-core`

The mock also includes one deliberately missing symbol reference so the placeholder and marker path can be exercised.

## Unit System
The preview now uses a shared scene unit system from `schematicMetrics.ts`.

Key points:
- `SCHEMATIC_UNIT` is the base conversion constant.
- `su()` is used to derive page size, symbol geometry, spacing, text size, and other metrics.
- viewport padding, grid step, title box geometry, stroke widths, radii, and text sizes are centralized.

This avoids mixing unrelated ad hoc dimensions across page, symbol, and viewport logic.

## Current Limitations
The preview is still a GUI demo and has clear scope limits.

Not yet implemented:
- real backend schematic source
- editable schematic authoring
- full symbol library support
- power/ground symbol families as dedicated symbol objects
- buses and bus entries
- hierarchical sheets or cross-page ports
- electrical-rule semantics in rendering
- hit testing and selection model
- layer visibility management
- print/export pipeline

## Current Interaction Notes
The current panel interaction model is optimized for previewing, not editing.

Behavior implemented today:
- drag uses manual viewport pan
- wheel zoom uses the mouse position as the zoom anchor
- drag suppresses browser text selection/highlight
- fit actions can reset back to deterministic page/content views

## Recommended Next Steps
- Replace mock geometry with a typed GUI adapter for real schematic output.
- Separate preview-only overlays from future editable interaction layers.
- Introduce explicit element IDs and hit-test metadata for selection and inspection.
- Expand the symbol and connectivity mock set before moving to editor interactions.
