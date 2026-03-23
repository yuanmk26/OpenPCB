import { AppHeader } from "./components/shell/AppHeader";
import { ChatColumn } from "./components/shell/ChatColumn";
import { Workspace } from "./components/workspace/Workspace";
import { RightPanel } from "./components/shell/RightPanel";

export default function App() {
  return (
    <div className="app-shell">
      <AppHeader />
      <div className="app-body">
        <ChatColumn />
        <Workspace />
        <RightPanel />
      </div>
    </div>
  );
}
