import type { SidebarItem } from "@/types/ui";

const items: SidebarItem[] = [
  { id: "project", label: "Project" },
  { id: "files", label: "Files" },
  { id: "steps", label: "Steps" }
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="panel-title">Navigation</div>
      <nav>
        <ul className="sidebar-list">
          {items.map((item) => (
            <li className="sidebar-item" key={item.id}>
              {item.label}
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
