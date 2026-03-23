import { ChatPanel } from "@/components/placeholders/ChatPanel";

export function ChatColumn() {
  return (
    <aside className="chat-column">
      <div className="panel-title">Chat</div>
      <div className="chat-column-body">
        <ChatPanel />
      </div>
    </aside>
  );
}
