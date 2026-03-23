import { PlannerStatus } from "@/components/placeholders/PlannerStatus";
import { ToolLogs } from "@/components/placeholders/ToolLogs";

export function RightPanel() {
  return (
    <aside className="right-panel">
      <PlannerStatus />
      <ToolLogs />
    </aside>
  );
}
