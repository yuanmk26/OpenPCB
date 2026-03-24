export type SidebarItem = {
  id: string;
  label: string;
};

export type WorkspaceView = "files" | "schematic" | "layout";

export type InfoPanelSection = "requirements" | "component-library" | "project-overview";

export type PlaceholderCard = {
  title: string;
  description: string;
};

export type SelectedSchematicComponent = {
  instanceId: string;
  refdes: string;
  value: string;
  symbolId: string;
  symbolName: string;
  pageId: string;
  pageTitle: string;
  isPlaceholder: boolean;
  statusMessage?: string;
};
