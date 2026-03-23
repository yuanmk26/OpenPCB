# OpenPCB GUI Subproject

## Purpose
`src/gui` is the desktop GUI skeleton for OpenPCB.  
It provides a runnable workbench shell for future integration with planner state, tool logs, and preview panels.

## Tech Stack
- Tauri v2
- React
- TypeScript
- Vite
- Plain CSS (no UI framework)

## Directory Layout
```text
src/gui/
  package.json
  index.html
  tsconfig.json
  vite.config.ts
  ui/
    App.tsx
    main.tsx
    components/
    styles/
    lib/
    types/
  src-tauri/
    Cargo.toml
    build.rs
    tauri.conf.json
    src/main.rs
```

## Start in Dev Mode
From repository root:
```bash
cd src/gui
npm install
npm run tauri dev
```

If PowerShell policy blocks `npm`, use:
```bash
npm.cmd install
npm.cmd run tauri dev
```

## Current Scope
- One desktop window titled `OpenPCB`
- Three-column workbench shell
- Header + Sidebar + Workspace + Right Panel
- Placeholder cards for requirement/chat/schematic/layout/planner/logs
- Tauri bridge entry placeholder in `ui/lib/tauri.ts`

## Next Extensions
- Add typed Tauri commands and events in `ui/lib/tauri.ts`
- Connect planner status and logs to runtime events
- Add schematic/layout render adapters
- Bridge Tauri commands to Python backend processes
