# OpenPCB GUI Roadmap

## Stage 1: Window and Base Layout
- Create Tauri desktop shell and React app entry.
- Deliver header/sidebar/workspace/right-panel structure.
- Keep each placeholder panel in separate component files.

## Stage 2: Tauri Bridge Placeholder
- Add `ui/lib/tauri.ts` as single bridge entry.
- Keep command/event wrappers minimal with TODOs for typed contracts.

## Stage 3: Status Panel and Logs
- Define baseline status/log data contracts.
- Connect planner status and tool logs panels to mock runtime events.

## Stage 4: Schematic Preview Placeholder
- Replace static schematic placeholder with render container.
- Define render adapter interface for future data source injection.

## Stage 5: Layout Preview Placeholder
- Replace static layout placeholder with render container.
- Add interaction hooks for zoom/layer/filter controls.

## Stage 6: Integrate Python Backend
- Implement Tauri-to-Python command bridge.
- Add request/response and streaming event channels.
- Connect requirement/chat/planner/preview flows to backend services.
