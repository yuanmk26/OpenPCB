import { useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { buildSchematicScene, fitViewportToBounds, getPageScene } from "@/lib/schematicScene";
import { loadSchematicGeometry } from "@/lib/schematicPreview";
import type {
  GraphicPrimitive,
  Point,
  ResolvedPin,
  SchematicPageScene,
  SchematicScene,
  SymbolDefinition,
  ViewportState
} from "@/types/schematic";

const GRID_STEP = 20;

export function SchematicPreview() {
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const dragState = useRef<{ active: boolean; pointerId: number; last: Point }>({
    active: false,
    pointerId: -1,
    last: { x: 0, y: 0 }
  });
  const [scene, setScene] = useState<SchematicScene | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [containerSize, setContainerSize] = useState({ width: 1, height: 1 });
  const [viewport, setViewport] = useState<ViewportState>({
    pageId: "",
    scale: 1,
    pan: { x: 0, y: 0 }
  });

  useEffect(() => {
    let cancelled = false;

    async function loadScene() {
      setIsLoading(true);
      setError(null);

      try {
        const geometry = await loadSchematicGeometry();

        if (cancelled) {
          return;
        }

        const nextScene = buildSchematicScene(geometry);
        const firstPage = nextScene.pages[0];
        setScene(nextScene);
        setViewport((current) => ({
          pageId: current.pageId || firstPage?.pageId || "",
          scale: current.scale,
          pan: current.pan
        }));
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load schematic preview.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadScene();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const element = viewportRef.current;

    if (!element) {
      return;
    }

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];

      if (!entry) {
        return;
      }

      setContainerSize({
        width: entry.contentRect.width,
        height: entry.contentRect.height
      });
    });

    observer.observe(element);

    return () => observer.disconnect();
  }, []);

  const activePage = useMemo(() => {
    if (!scene) {
      return null;
    }

    return getPageScene(scene, viewport.pageId) ?? scene.pages[0] ?? null;
  }, [scene, viewport.pageId]);

  useEffect(() => {
    if (!activePage) {
      return;
    }

    const fitted = fitViewportToBounds(
      activePage.contentBounds ?? activePage.bounds,
      containerSize,
      activePage.size
    );
    setViewport((current) => ({
      pageId: activePage.pageId,
      scale: fitted.scale,
      pan: fitted.pan
    }));
  }, [activePage?.pageId, activePage?.size.height, activePage?.size.width, containerSize.height, containerSize.width]);

  function handleFitToPage() {
    if (!activePage) {
      return;
    }

    const fitted = fitViewportToBounds(
      activePage.contentBounds ?? activePage.bounds,
      containerSize,
      activePage.size
    );
    setViewport((current) => ({
      ...current,
      scale: fitted.scale,
      pan: fitted.pan
    }));
  }

  function handleZoom(multiplier: number) {
    setViewport((current) => ({
      ...current,
      scale: Math.min(Math.max(Number((current.scale * multiplier).toFixed(3)), 0.25), 4)
    }));
  }

  function handleReset() {
    handleFitToPage();
  }

  function handlePointerDown(event: ReactPointerEvent<SVGSVGElement>) {
    dragState.current = {
      active: true,
      pointerId: event.pointerId,
      last: { x: event.clientX, y: event.clientY }
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function handlePointerMove(event: ReactPointerEvent<SVGSVGElement>) {
    if (!dragState.current.active || dragState.current.pointerId !== event.pointerId) {
      return;
    }

    const deltaX = event.clientX - dragState.current.last.x;
    const deltaY = event.clientY - dragState.current.last.y;

    dragState.current.last = { x: event.clientX, y: event.clientY };

    setViewport((current) => ({
      ...current,
      pan: {
        x: current.pan.x + deltaX,
        y: current.pan.y + deltaY
      }
    }));
  }

  function handlePointerUp(event: ReactPointerEvent<SVGSVGElement>) {
    if (dragState.current.pointerId === event.pointerId) {
      dragState.current.active = false;
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  }

  if (isLoading) {
    return (
      <section className="schematic-viewer">
        <div className="schematic-viewer-empty">
          <h3>Loading Preview</h3>
          <p>Preparing the schematic page and symbol scene.</p>
        </div>
      </section>
    );
  }

  if (error || !scene || !activePage) {
    return (
      <section className="schematic-viewer">
        <div className="schematic-viewer-empty">
          <h3>Schematic Preview</h3>
          <p>{error ?? "No schematic geometry is available."}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="schematic-viewer">
      <div className="schematic-toolbar">
        <div className="schematic-toolbar-group">
          {scene.pages.map((page) => (
            <button
              type="button"
              key={page.pageId}
              className={`schematic-chip ${page.pageId === activePage.pageId ? "is-active" : ""}`}
              onClick={() => setViewport((current) => ({ ...current, pageId: page.pageId }))}
            >
              {page.title}
            </button>
          ))}
        </div>
        <div className="schematic-toolbar-group">
          <button type="button" className="schematic-chip" onClick={() => handleZoom(1.2)}>
            Zoom In
          </button>
          <button type="button" className="schematic-chip" onClick={() => handleZoom(1 / 1.2)}>
            Zoom Out
          </button>
          <button type="button" className="schematic-chip" onClick={handleReset}>
            Fit
          </button>
        </div>
      </div>
      <div className="schematic-stage" ref={viewportRef}>
        <svg
          className="schematic-canvas"
          viewBox={`0 0 ${containerSize.width} ${containerSize.height}`}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={handlePointerUp}
        >
          <defs>
            <pattern id="schematic-grid" width={GRID_STEP} height={GRID_STEP} patternUnits="userSpaceOnUse">
              <path d={`M ${GRID_STEP} 0 L 0 0 0 ${GRID_STEP}`} fill="none" stroke="#eef2f7" strokeWidth="0.6" />
            </pattern>
          </defs>
          <rect x={0} y={0} width={containerSize.width} height={containerSize.height} fill="#d5dbe3" />
          <g transform={`translate(${viewport.pan.x} ${viewport.pan.y}) scale(${viewport.scale})`}>
            <rect
              x={0}
              y={0}
              width={activePage.size.width}
              height={activePage.size.height}
              fill="#fdfdfc"
              stroke="#6b7280"
              strokeWidth={1.2}
            />
            <rect
              x={18}
              y={18}
              width={activePage.size.width - 36}
              height={activePage.size.height - 36}
              fill="url(#schematic-grid)"
              opacity={0.55}
            />
            <PageFrame page={activePage} />
            <PageWires page={activePage} />
            <PageJunctions page={activePage} />
            <PageSymbols page={activePage} />
            <PageLabels page={activePage} />
            <PageMarkers page={activePage} />
          </g>
        </svg>
      </div>
      <div className="schematic-statusbar">
        <span>{scene.metadata.title ?? "Schematic Preview"}</span>
        <span>
          {activePage.title} - {activePage.size.width} x {activePage.size.height}
        </span>
        <span>{Math.round(viewport.scale * 100)}%</span>
      </div>
    </section>
  );
}

function PageFrame({ page }: { page: SchematicPageScene }) {
  const titleBoxWidth = 340;
  const titleBoxHeight = 90;
  const titleBoxX = page.size.width - titleBoxWidth - 28;
  const titleBoxY = page.size.height - titleBoxHeight - 24;

  return (
    <g className="schematic-layer-frame">
      <rect x={22} y={22} width={page.size.width - 44} height={page.size.height - 44} fill="none" stroke="#9ca3af" strokeWidth={0.8} />
      <rect x={titleBoxX} y={titleBoxY} width={titleBoxWidth} height={titleBoxHeight} fill="none" stroke="#6b7280" strokeWidth={0.8} />
      <line x1={titleBoxX} y1={titleBoxY + 28} x2={titleBoxX + titleBoxWidth} y2={titleBoxY + 28} stroke="#6b7280" strokeWidth={0.8} />
      <line x1={titleBoxX + 96} y1={titleBoxY + 28} x2={titleBoxX + 96} y2={titleBoxY + titleBoxHeight} stroke="#6b7280" strokeWidth={0.8} />
      <text className="schematic-title" x={40} y={52}>
        {page.title}
      </text>
      <text className="schematic-sheet-meta" x={titleBoxX + 12} y={titleBoxY + 18}>
        TITLE
      </text>
      <text className="schematic-sheet-value" x={titleBoxX + 12} y={titleBoxY + 52}>
        {page.title}
      </text>
      <text className="schematic-sheet-meta" x={titleBoxX + 108} y={titleBoxY + 18}>
        SHEET
      </text>
      <text className="schematic-sheet-value" x={titleBoxX + 108} y={titleBoxY + 52}>
        {page.pageId}
      </text>
    </g>
  );
}

function PageWires({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-wires">
      {page.wires.map((wire) => (
        <polyline
          key={wire.wireId}
          points={wire.points.map((point) => `${point.x},${point.y}`).join(" ")}
          fill="none"
          stroke={wire.style === "power" || wire.style === "ground" ? "#111827" : "#1f2937"}
          strokeWidth={wire.style === "clock" ? 1.8 : 1.4}
          strokeLinejoin="miter"
          strokeLinecap="square"
          vectorEffect="non-scaling-stroke"
        />
      ))}
    </g>
  );
}

function PageJunctions({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-junctions">
      {page.junctions.map((junction) => (
        <circle
          key={junction.junctionId}
          cx={junction.position.x}
          cy={junction.position.y}
          r={3.4}
          fill="#111827"
          vectorEffect="non-scaling-stroke"
        />
      ))}
    </g>
  );
}

function PageSymbols({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-symbols">
      {page.instances.map((instance) => (
        <g key={instance.instanceId}>
          <g transform={instance.transform}>
            {instance.symbol.graphics.map((graphic) => (
              <SymbolGraphic key={graphic.id} primitive={graphic} symbol={instance.symbol} />
            ))}
          </g>
          <text className="schematic-refdes" x={instance.refdesPosition.x} y={instance.refdesPosition.y}>
            {instance.refdes}
          </text>
          <text className="schematic-value" x={instance.valuePosition.x} y={instance.valuePosition.y}>
            {instance.value}
          </text>
          {instance.placeholderMessage ? (
            <text className="schematic-placeholder-message" x={instance.bounds.x + 8} y={instance.bounds.y + instance.bounds.height + 32}>
              {instance.placeholderMessage}
            </text>
          ) : null}
          {instance.renderedPins.map((pin) => (
            <PinText key={pin.pinId} pin={pin} />
          ))}
        </g>
      ))}
    </g>
  );
}

function PageLabels({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-labels">
      {page.labels.map((label) => (
        <text
          key={label.labelId}
          className="schematic-net-label"
          x={label.position.x}
          y={label.position.y}
          transform={label.orientation === 0 ? undefined : `rotate(${label.orientation} ${label.position.x} ${label.position.y})`}
        >
          {label.text}
        </text>
      ))}
    </g>
  );
}

function PageMarkers({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-markers">
      {page.markers.map((marker) => (
        <g key={marker.markerId} transform={`translate(${marker.position.x} ${marker.position.y})`}>
          <circle r={6} fill="#f59e0b" stroke="#78350f" strokeWidth={0.8} vectorEffect="non-scaling-stroke" />
          <text className="schematic-marker-text" x={0} y={2.8} textAnchor="middle">
            !
          </text>
        </g>
      ))}
    </g>
  );
}

function PinText({ pin }: { pin: ResolvedPin }) {
  return (
    <g className="schematic-pin-text">
      <text className="schematic-pin-name" x={pin.labelPosition.x} y={pin.labelPosition.y} textAnchor={pin.labelAnchor}>
        {pin.name}
      </text>
      <text className="schematic-pin-number" x={pin.numberPosition.x} y={pin.numberPosition.y} textAnchor={pin.numberAnchor}>
        {pin.number}
      </text>
    </g>
  );
}

function SymbolGraphic({
  primitive,
  symbol
}: {
  primitive: GraphicPrimitive;
  symbol: SymbolDefinition;
}) {
  switch (primitive.type) {
    case "line":
      return (
        <line
          x1={primitive.start.x}
          y1={primitive.start.y}
          x2={primitive.end.x}
          y2={primitive.end.y}
          stroke={normalizeStrokeColor(primitive.stroke)}
          strokeWidth={primitive.strokeWidth ?? 1.4}
          strokeLinecap="square"
          vectorEffect="non-scaling-stroke"
        />
      );
    case "pin_stub":
      return (
        <line
          x1={primitive.start.x}
          y1={primitive.start.y}
          x2={primitive.end.x}
          y2={primitive.end.y}
          stroke={normalizeStrokeColor(primitive.stroke)}
          strokeWidth={primitive.strokeWidth ?? 1.4}
          strokeLinecap="square"
          vectorEffect="non-scaling-stroke"
        />
      );
    case "rect":
      return (
        <rect
          x={primitive.origin.x}
          y={primitive.origin.y}
          width={primitive.width}
          height={primitive.height}
          fill={primitive.fill ?? "none"}
          stroke={normalizeStrokeColor(primitive.stroke)}
          strokeWidth={primitive.strokeWidth ?? 1.4}
          vectorEffect="non-scaling-stroke"
        />
      );
    case "circle":
      return (
        <circle
          cx={primitive.center.x}
          cy={primitive.center.y}
          r={primitive.radius}
          fill={primitive.fill ?? "none"}
          stroke={normalizeStrokeColor(primitive.stroke)}
          strokeWidth={primitive.strokeWidth ?? 1.4}
          vectorEffect="non-scaling-stroke"
        />
      );
    case "polyline":
      return (
        <polyline
          points={primitive.points.map((point) => `${point.x},${point.y}`).join(" ")}
          fill={primitive.fill ?? "none"}
          stroke={normalizeStrokeColor(primitive.stroke)}
          strokeWidth={primitive.strokeWidth ?? 1.4}
          strokeLinejoin="miter"
          strokeLinecap="square"
          vectorEffect="non-scaling-stroke"
        />
      );
    case "text":
      return (
        <text
          x={primitive.position.x}
          y={primitive.position.y}
          fontSize={primitive.fontSize ?? 12}
          fill="#111827"
          textAnchor={primitive.anchor ?? "start"}
        >
          {primitive.text}
        </text>
      );
  }

  return (
    <text x={symbol.bounds.x} y={symbol.bounds.y} fill="#b91c1c">
      Unsupported primitive
    </text>
  );
}

function normalizeStrokeColor(stroke?: string): string {
  if (!stroke) {
    return "#111827";
  }

  const normalized = stroke.trim().toLowerCase();

  if (normalized === "#dfe8f1" || normalized === "#eef2f7" || normalized === "#ffffff") {
    return "#111827";
  }

  return stroke;
}
