import type { SelectedSchematicItem } from "@/types/ui";

type SchematicComponentInfoPanelProps = {
  item: SelectedSchematicItem | null;
};

export function SchematicComponentInfoPanel({ item }: SchematicComponentInfoPanelProps) {
  if (!item) {
    return (
      <section className="placeholder-card right-card schematic-component-panel is-empty">
        <h3>Selection Info</h3>
        <p>Click a component or net label to inspect its details.</p>
      </section>
    );
  }

  if (item.kind === "net") {
    return (
      <section className="placeholder-card right-card schematic-component-panel">
        <div className="schematic-component-panel-header">
          <h3>{item.name}</h3>
          <span className="schematic-component-badge">Net</span>
        </div>
        <dl className="schematic-component-meta">
          <div>
            <dt>Net ID</dt>
            <dd>{item.netId}</dd>
          </div>
          <div>
            <dt>Style</dt>
            <dd>{item.style}</dd>
          </div>
          <div>
            <dt>Page</dt>
            <dd>{item.pageTitle}</dd>
          </div>
          <div>
            <dt>Label Count</dt>
            <dd>{item.labelCount}</dd>
          </div>
        </dl>
        {item.statusMessage ? <p className="schematic-component-status">{item.statusMessage}</p> : null}
      </section>
    );
  }

  return (
    <section className="placeholder-card right-card schematic-component-panel">
      <div className="schematic-component-panel-header">
        <h3>{item.refdes}</h3>
        <span className={`schematic-component-badge ${item.isPlaceholder ? "is-warning" : ""}`}>
          {item.isPlaceholder ? "Placeholder" : "Component"}
        </span>
      </div>
      <dl className="schematic-component-meta">
        <div>
          <dt>Value</dt>
          <dd>{item.value}</dd>
        </div>
        <div>
          <dt>Component</dt>
          <dd>{item.symbolName}</dd>
        </div>
        <div>
          <dt>Symbol ID</dt>
          <dd>{item.symbolId}</dd>
        </div>
        <div>
          <dt>Page</dt>
          <dd>{item.pageTitle}</dd>
        </div>
      </dl>
      {item.statusMessage ? <p className="schematic-component-status">{item.statusMessage}</p> : null}
    </section>
  );
}
