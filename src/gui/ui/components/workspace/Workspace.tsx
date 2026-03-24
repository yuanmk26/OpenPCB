import { useMemo } from "react";
import { FilesPanel } from "@/components/placeholders/FilesPanel";
import { SchematicPreview } from "@/components/placeholders/SchematicPreview";
import { LayoutPreview } from "@/components/placeholders/LayoutPreview";
import type { SelectedSchematicItem, WorkspaceView } from "@/types/ui";

const workspaceTabs: Array<{ id: WorkspaceView; label: string }> = [
  { id: "files", label: "Files" },
  { id: "schematic", label: "Schematic Preview" },
  { id: "layout", label: "Layout Preview" }
];

type WorkspaceProps = {
  activeView: WorkspaceView;
  onActiveViewChange: (view: WorkspaceView) => void;
  selectedItem: SelectedSchematicItem | null;
  onSelectItem: (item: SelectedSchematicItem | null) => void;
};

export function Workspace({
  activeView,
  onActiveViewChange,
  selectedItem,
  onSelectItem
}: WorkspaceProps) {
  const activePanel = useMemo(() => {
    if (activeView === "schematic") {
      return (
        <SchematicPreview
          selectedItem={selectedItem}
          onSelectItem={onSelectItem}
        />
      );
    }

    if (activeView === "layout") {
      return <LayoutPreview />;
    }

    return <FilesPanel />;
  }, [activeView, onSelectItem, selectedItem]);

  return (
    <main className="workspace">
      <div className="workspace-header">
        <h2>OpenPCB Workspace</h2>
        <div className="workspace-view-bar" role="tablist" aria-label="Workspace Views">
          {workspaceTabs.map((tab) => (
            <button
              type="button"
              key={tab.id}
              role="tab"
              aria-selected={activeView === tab.id}
              className={`workspace-view-tab ${activeView === tab.id ? "is-active" : ""}`}
              onClick={() => onActiveViewChange(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      <div className="workspace-content">
        {activePanel}
      </div>
    </main>
  );
}
