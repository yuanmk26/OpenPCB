import { RequirementPanel } from "@/components/placeholders/RequirementPanel";
import { ComponentLibraryPanel } from "@/components/placeholders/ComponentLibraryPanel";
import { ProjectOverviewPanel } from "@/components/placeholders/ProjectOverviewPanel";

export function RightPanel() {
  return (
    <aside className="right-panel">
      <div className="panel-title">Project Info</div>
      <div className="right-panel-content">
        <RequirementPanel />
        <ComponentLibraryPanel />
        <ProjectOverviewPanel />
      </div>
    </aside>
  );
}
