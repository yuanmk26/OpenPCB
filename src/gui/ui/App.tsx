import { useState } from "react";
import { AppHeader } from "./components/shell/AppHeader";
import { ChatColumn } from "./components/shell/ChatColumn";
import { Workspace } from "./components/workspace/Workspace";
import { RightPanel } from "./components/shell/RightPanel";
import type { SelectedSchematicComponent, WorkspaceView } from "./types/ui";

export default function App() {
  const [activeView, setActiveView] = useState<WorkspaceView>("files");
  const [selectedComponent, setSelectedComponent] = useState<SelectedSchematicComponent | null>(null);

  function handleActiveViewChange(view: WorkspaceView) {
    setActiveView(view);

    if (view !== "schematic") {
      setSelectedComponent(null);
    }
  }

  return (
    <div className="app-shell">
      <AppHeader />
      <div className="app-body">
        <ChatColumn />
        <Workspace
          activeView={activeView}
          onActiveViewChange={handleActiveViewChange}
          selectedComponent={selectedComponent}
          onSelectComponent={setSelectedComponent}
        />
        <RightPanel activeView={activeView} selectedComponent={selectedComponent} />
      </div>
    </div>
  );
}
