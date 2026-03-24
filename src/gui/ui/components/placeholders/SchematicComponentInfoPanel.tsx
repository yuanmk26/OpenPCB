import type { SelectedSchematicComponent } from "@/types/ui";

type SchematicComponentInfoPanelProps = {
  component: SelectedSchematicComponent | null;
};

export function SchematicComponentInfoPanel({ component }: SchematicComponentInfoPanelProps) {
  if (!component) {
    return (
      <section className="placeholder-card right-card schematic-component-panel is-empty">
        <h3>Component Info</h3>
        <p>Click a component to inspect its details.</p>
      </section>
    );
  }

  return (
    <section className="placeholder-card right-card schematic-component-panel">
      <div className="schematic-component-panel-header">
        <h3>{component.refdes}</h3>
        <span className={`schematic-component-badge ${component.isPlaceholder ? "is-warning" : ""}`}>
          {component.isPlaceholder ? "Placeholder" : "Selected"}
        </span>
      </div>
      <dl className="schematic-component-meta">
        <div>
          <dt>Value</dt>
          <dd>{component.value}</dd>
        </div>
        <div>
          <dt>Component</dt>
          <dd>{component.symbolName}</dd>
        </div>
        <div>
          <dt>Symbol ID</dt>
          <dd>{component.symbolId}</dd>
        </div>
        <div>
          <dt>Page</dt>
          <dd>{component.pageTitle}</dd>
        </div>
      </dl>
      {component.statusMessage ? <p className="schematic-component-status">{component.statusMessage}</p> : null}
    </section>
  );
}
