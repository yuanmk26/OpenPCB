import { useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { buildSchematicScene, fitViewport, getPageScene } from "@/lib/schematicScene";
import { loadSchematicGeometry } from "@/lib/schematicPreview";
import type {
  GraphicPrimitive,
  Point,
  SchematicPageScene,
  SchematicScene,
  SymbolDefinition,
  ViewportState
} from "@/types/schematic";

const GRID_STEP = 40;

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

    const fitted = fitViewport(activePage.size, containerSize);
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

    const fitted = fitViewport(activePage.size, containerSize);
    setViewport((current) => ({
      ...current,
      scale: fitted.scale,
      pan: fitted.pan
    }));
  }

  function handleZoom(multiplier: number) {
    setViewport((current) => ({
      ...current,
      scale: Math.min(Math.max(Number((current.scale * multiplier).toFixed(3)), 0.2), 4)
    }));
  }

  function handleReset() {
    setViewport((current) => ({
      ...current,
      scale: 1,
      pan: { x: 32, y: 32 }
    }));
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
          <p>Preparing the geometry scene for SVG rendering.</p>
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
            Reset
          </button>
          <button type="button" className="schematic-chip" onClick={handleFitToPage}>
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
              <path d={`M ${GRID_STEP} 0 L 0 0 0 ${GRID_STEP}`} fill="none" stroke="#1d3045" strokeWidth="1" />
            </pattern>
          </defs>
          <g transform={`translate(${viewport.pan.x} ${viewport.pan.y}) scale(${viewport.scale})`}>
            <rect
              x={0}
              y={0}
              width={activePage.size.width}
              height={activePage.size.height}
              fill="#0f1720"
              stroke="#355170"
              strokeWidth={2}
              rx={16}
            />
            <rect
              x={0}
              y={0}
              width={activePage.size.width}
              height={activePage.size.height}
              fill="url(#schematic-grid)"
              opacity={0.65}
            />
            <text x={30} y={44} fill="#8ea3ba" fontSize={22}>
              {activePage.title}
            </text>
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

function PageWires({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-wires">
      {page.wires.map((wire) => (
        <polyline
          key={wire.wireId}
          points={wire.points.map((point) => `${point.x},${point.y}`).join(" ")}
          fill="none"
          stroke={wire.style === "power" ? "#78c6ff" : wire.style === "ground" ? "#9bd37a" : "#e6edf4"}
          strokeWidth={wire.style === "clock" ? 3.2 : 2.4}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      ))}
    </g>
  );
}

function PageJunctions({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-junctions">
      {page.junctions.map((junction) => (
        <circle key={junction.junctionId} cx={junction.position.x} cy={junction.position.y} r={5} fill="#dfe8f1" />
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
        </g>
      ))}
    </g>
  );
}

function PageLabels({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-labels">
      {page.labels.map((label) => (
        <g
          key={label.labelId}
          transform={`translate(${label.position.x} ${label.position.y}) rotate(${label.orientation})`}
        >
          <rect x={-8} y={-18} width={label.text.length * 10 + 16} height={24} rx={8} fill="#19314b" opacity={0.95} />
          <text className="schematic-net-label" x={0} y={0}>
            {label.text}
          </text>
        </g>
      ))}
    </g>
  );
}

function PageMarkers({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-layer-markers">
      {page.markers.map((marker) => (
        <g key={marker.markerId} transform={`translate(${marker.position.x} ${marker.position.y})`}>
          <circle r={12} fill={marker.kind === "error" ? "#c83f49" : marker.kind === "warning" ? "#c88e27" : "#2d7dd2"} />
          <text className="schematic-marker-text" x={0} y={5} textAnchor="middle">
            !
          </text>
          <text className="schematic-marker-message" x={18} y={6}>
            {marker.message}
          </text>
        </g>
      ))}
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
          stroke={primitive.stroke ?? "#dfe8f1"}
          strokeWidth={primitive.strokeWidth ?? 2}
        />
      );
    case "pin_stub":
      return (
        <line
          x1={primitive.start.x}
          y1={primitive.start.y}
          x2={primitive.end.x}
          y2={primitive.end.y}
          stroke={primitive.stroke ?? "#dfe8f1"}
          strokeWidth={primitive.strokeWidth ?? 2.4}
          strokeLinecap="round"
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
          stroke={primitive.stroke ?? "#dfe8f1"}
          strokeWidth={primitive.strokeWidth ?? 2}
          rx={6}
        />
      );
    case "circle":
      return (
        <circle
          cx={primitive.center.x}
          cy={primitive.center.y}
          r={primitive.radius}
          fill={primitive.fill ?? "none"}
          stroke={primitive.stroke ?? "#dfe8f1"}
          strokeWidth={primitive.strokeWidth ?? 2}
        />
      );
    case "polyline":
      return (
        <polyline
          points={primitive.points.map((point) => `${point.x},${point.y}`).join(" ")}
          fill={primitive.fill ?? "none"}
          stroke={primitive.stroke ?? "#dfe8f1"}
          strokeWidth={primitive.strokeWidth ?? 2}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      );
    case "text":
      return (
        <text
          x={primitive.position.x}
          y={primitive.position.y}
          fontSize={primitive.fontSize ?? 14}
          fill="#dfe8f1"
          textAnchor={primitive.anchor ?? "start"}
        >
          {primitive.text}
        </text>
      );
  }

  return (
    <text x={symbol.bounds.x} y={symbol.bounds.y} fill="#c83f49">
      Unsupported primitive
    </text>
  );
}
