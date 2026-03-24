import { RequirementPanel } from "@/components/placeholders/RequirementPanel";
import { ComponentLibraryPanel } from "@/components/placeholders/ComponentLibraryPanel";
import { ProjectOverviewPanel } from "@/components/placeholders/ProjectOverviewPanel";
import { SchematicComponentInfoPanel } from "@/components/placeholders/SchematicComponentInfoPanel";
import type { SelectedSchematicComponent, WorkspaceView } from "@/types/ui";

type RightPanelProps = {
  activeView: WorkspaceView;
  selectedComponent: SelectedSchematicComponent | null;
};

export function RightPanel({ activeView, selectedComponent }: RightPanelProps) {
  return (
    <aside className="right-panel">
      <div className="panel-title">{activeView === "schematic" ? "Component Info" : "Project Info"}</div>
      <div className="right-panel-content">
        {activeView === "schematic" ? (
          <SchematicComponentInfoPanel component={selectedComponent} />
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
