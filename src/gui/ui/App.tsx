import { AppHeader } from "./components/shell/AppHeader";
import { Sidebar } from "./components/shell/Sidebar";
import { Workspace } from "./components/workspace/Workspace";
import { RightPanel } from "./components/shell/RightPanel";

export default function App() {
  return (
    <div className="app-shell">
      <AppHeader />
      <div className="app-body">
        <Sidebar />
        <Workspace />
        <RightPanel />
      </div>
    </div>
  );
}
