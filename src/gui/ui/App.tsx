import { useState } from "react";
import { AppHeader } from "./components/shell/AppHeader";
import { ChatColumn } from "./components/shell/ChatColumn";
import { Workspace } from "./components/workspace/Workspace";
import { RightPanel } from "./components/shell/RightPanel";
import type { SelectedSchematicItem, WorkspaceView } from "./types/ui";

export default function App() {
  const [activeView, setActiveView] = useState<WorkspaceView>("files");
  const [selectedItem, setSelectedItem] = useState<SelectedSchematicItem | null>(null);

  function handleActiveViewChange(view: WorkspaceView) {
    setActiveView(view);

    if (view !== "schematic") {
      setSelectedItem(null);
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
          selectedItem={selectedItem}
          onSelectItem={setSelectedItem}
        />
        <RightPanel activeView={activeView} selectedItem={selectedItem} />
      </div>
    </div>
  );
}
