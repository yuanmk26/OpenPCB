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
  kind: "component";
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

export type SelectedSchematicNet = {
  kind: "net";
  netId: string;
  name: string;
  style: string;
  pageId: string;
  pageTitle: string;
  labelId: string;
  labelText: string;
  labelCount: number;
  statusMessage?: string;
};

export type SelectedSchematicItem = SelectedSchematicComponent | SelectedSchematicNet;
