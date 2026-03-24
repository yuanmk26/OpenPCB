import { RequirementPanel } from "@/components/placeholders/RequirementPanel";
import { ComponentLibraryPanel } from "@/components/placeholders/ComponentLibraryPanel";
import { ProjectOverviewPanel } from "@/components/placeholders/ProjectOverviewPanel";
import { SchematicComponentInfoPanel } from "@/components/placeholders/SchematicComponentInfoPanel";
import type { SelectedSchematicItem, WorkspaceView } from "@/types/ui";

type RightPanelProps = {
  activeView: WorkspaceView;
  selectedItem: SelectedSchematicItem | null;
};

export function RightPanel({ activeView, selectedItem }: RightPanelProps) {
  return (
    <aside className="right-panel">
      <div className="panel-title">{activeView === "schematic" ? "Selection Info" : "Project Info"}</div>
      <div className="right-panel-content">
        {activeView === "schematic" ? (
          <SchematicComponentInfoPanel item={selectedItem} />
        ) : (
          <>
            <RequirementPanel />
            <ComponentLibraryPanel />
            <ProjectOverviewPanel />
          </>
        )}
      </div>
    </aside>
  );
}
