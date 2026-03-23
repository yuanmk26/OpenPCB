# GUI Architecture Notes

## Why Tauri + React + TypeScript + Vite
- Tauri v2 keeps desktop runtime lightweight and secure, with Rust-native host capabilities.
- React gives fast composition for panel-based engineering UI.
- TypeScript improves long-term maintainability for UI contracts and command payloads.
- Vite provides fast local iteration and simple build output for Tauri integration.

## Relation to Python Main Project
- Existing Python code under `src/openpcb` remains the core orchestration/toolchain module.
- GUI is a sibling submodule under `src/gui`, isolated from Python package layout.
- Future interaction path:
  1. UI emits actions
  2. Tauri bridge translates to commands/events
  3. Tauri host triggers backend bridge to Python runtime

## Layered Structure
- `ui/components/*`: visual workbench shell and panels
- `ui/lib/tauri.ts`: frontend bridge entry for invoke/event APIs
- `ui/types/*`: shared UI-facing type contracts
- `src-tauri/*`: desktop host and app/window config

## UI / Bridge / Future Backend Flow
1. User interacts with panel component.
2. Component calls bridge helper in `ui/lib/tauri.ts`.
3. Bridge invokes Tauri command or subscribes event channel.
4. Tauri side will later proxy to Python service/process layer.
5. UI updates from typed event payloads.

## Extension Locations
- Schematic preview evolution: `ui/components/placeholders/SchematicPreview.tsx`
- Layout preview evolution: `ui/components/placeholders/LayoutPreview.tsx`
- Planner runtime status integration: `ui/components/placeholders/PlannerStatus.tsx`
- Tool execution streaming integration: `ui/components/placeholders/ToolLogs.tsx`
