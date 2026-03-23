import { RequirementPanel } from "@/components/placeholders/RequirementPanel";
import { ChatPanel } from "@/components/placeholders/ChatPanel";
import { SchematicPreview } from "@/components/placeholders/SchematicPreview";
import { LayoutPreview } from "@/components/placeholders/LayoutPreview";

export function Workspace() {
  return (
    <main className="workspace">
      <div className="workspace-header">
        <h2>OpenPCB Workspace</h2>
      </div>
      <div className="workspace-grid">
        <RequirementPanel />
        <ChatPanel />
        <SchematicPreview />
        <LayoutPreview />
      </div>
    </main>
  );
}
