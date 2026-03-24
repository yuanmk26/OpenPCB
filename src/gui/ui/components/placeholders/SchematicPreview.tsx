import { useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { buildSchematicScene, fitViewportToContent, fitViewportToPage, getPageScene } from "@/lib/schematicScene";
import {
  SCHEMATIC_PAGE_FRAME_INSET,
  SCHEMATIC_PAGE_GRID_STEP,
  SCHEMATIC_PAGE_INNER_INSET,
  SCHEMATIC_RADIUS,
  SCHEMATIC_STROKE,
  SCHEMATIC_TEXT,
  SCHEMATIC_TITLE_BOX,
  su
} from "@/lib/schematicMetrics";
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

const GRID_STEP = SCHEMATIC_PAGE_GRID_STEP;

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
  const [debugEnabled, setDebugEnabled] = useState(false);
  const [viewport, setViewport] = useState<ViewportState>({
    pageId: "",
    scale: 1,
    pan: { x: 0, y: 0 },
    mode: "page"
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
          pan: current.pan,
          mode: current.mode
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

    const updateContainerSize = () => {
      const rect = element.getBoundingClientRect();
      setContainerSize({
        width: Math.max(Math.round(rect.width), 1),
        height: Math.max(Math.round(rect.height), 1)
      });
    };

    updateContainerSize();

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];

      if (!entry) {
        updateContainerSize();
        return;
      }

      const nextWidth = Math.max(Math.round(entry.contentRect.width), 1);
      const nextHeight = Math.max(Math.round(entry.contentRect.height), 1);

      if (nextWidth <= 1 || nextHeight <= 1) {
        updateContainerSize();
        return;
      }

      setContainerSize({
        width: nextWidth,
        height: nextHeight
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

  const renderSummary = useMemo(() => {
    if (!activePage) {
      return null;
    }

    return {
      instances: activePage.instances.length,
      symbolGraphics: activePage.instances.reduce((count, instance) => count + instance.symbol.graphics.length, 0),
      wires: activePage.wires.length,
      labels: activePage.labels.length,
      junctions: activePage.junctions.length,
      markers: activePage.markers.length
    };
  }, [activePage]);

  useEffect(() => {
    if (!activePage) {
      return;
    }

    const fitted =
      viewport.mode === "page"
        ? fitViewportToPage(activePage.bounds, containerSize)
        : fitViewportToContent(activePage.contentBounds ?? activePage.bounds, activePage.bounds, containerSize);
    setViewport((current) => ({
      pageId: activePage.pageId,
      scale: fitted.scale,
      pan: fitted.pan,
      mode: current.mode
    }));
  }, [activePage?.pageId, activePage?.size.height, activePage?.size.width, containerSize.height, containerSize.width, viewport.mode]);

  function handleFitContent() {
    if (!activePage) {
      return;
    }

    const fitted = fitViewportToContent(activePage.contentBounds ?? activePage.bounds, activePage.bounds, containerSize);
    setViewport((current) => ({
      ...current,
      scale: fitted.scale,
      pan: fitted.pan,
      mode: "content"
    }));
  }

  function handleFitPage() {
    if (!activePage) {
      return;
    }

    const fitted = fitViewportToPage(activePage.bounds, containerSize);
    setViewport((current) => ({
      ...current,
      scale: fitted.scale,
      pan: fitted.pan,
      mode: "page"
    }));
  }

  function handleZoom(multiplier: number) {
    setViewport((current) => ({
      ...current,
      scale: Math.min(Math.max(Number((current.scale * multiplier).toFixed(3)), 0.25), 4)
    }));
  }

  function handleReset() {
    handleFitPage();
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
          <button
            type="button"
            className={`schematic-chip ${debugEnabled ? "is-active" : ""}`}
            onClick={() => setDebugEnabled((current) => !current)}
          >
            Debug
          </button>
          <button type="button" className="schematic-chip" onClick={() => handleZoom(1.2)}>
            Zoom In
          </button>
          <button type="button" className="schematic-chip" onClick={() => handleZoom(1 / 1.2)}>
            Zoom Out
          </button>
          <button type="button" className="schematic-chip" onClick={handleFitContent}>
            Fit Content
          </button>
          <button type="button" className="schematic-chip" onClick={handleFitPage}>
            Fit Page
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
              <path d={`M ${GRID_STEP} 0 L 0 0 0 ${GRID_STEP}`} fill="none" stroke="#d8e0e8" strokeWidth="0.35" />
            </pattern>
          </defs>
          <rect x={0} y={0} width={containerSize.width} height={containerSize.height} fill="#d5dbe3" />
          {debugEnabled ? <DebugScreenGrid width={containerSize.width} height={containerSize.height} /> : null}
          <g transform={`translate(${viewport.pan.x} ${viewport.pan.y})`}>
            <g transform={`scale(${viewport.scale})`}>
              <rect
                x={0}
                y={0}
                width={activePage.size.width}
                height={activePage.size.height}
                fill="#fdfdfc"
                stroke="#6b7280"
                strokeWidth={SCHEMATIC_STROKE.pageBorder}
              />
              <rect
                x={SCHEMATIC_PAGE_INNER_INSET}
                y={SCHEMATIC_PAGE_INNER_INSET}
                width={activePage.size.width - SCHEMATIC_PAGE_INNER_INSET * 2}
                height={activePage.size.height - SCHEMATIC_PAGE_INNER_INSET * 2}
                fill="url(#schematic-grid)"
                opacity={0.32}
              />
              <LocatorCircle />
              <PageFrame page={activePage} />
              <PageWires page={activePage} />
              <PageJunctions page={activePage} />
              <PageSymbols page={activePage} />
              <PageLabels page={activePage} />
              <PageMarkers page={activePage} />
              {debugEnabled ? <DiagnosticFixture /> : null}
              {debugEnabled ? <DebugOverlay page={activePage} /> : null}
            </g>
          </g>
        </svg>
      </div>
      <div className="schematic-statusbar">
        <span>{scene.metadata.title ?? "Schematic Preview"}</span>
        <span>
          {activePage.title} - {activePage.size.width} x {activePage.size.height}
        </span>
        <span>
          {viewport.mode} · {Math.round(viewport.scale * 100)}% · pan({Math.round(viewport.pan.x)},{Math.round(viewport.pan.y)})
        </span>
        {renderSummary ? (
          <span>
            instances[{renderSummary.instances}] graphics[{renderSummary.symbolGraphics}] wires[{renderSummary.wires}] labels[{renderSummary.labels}] junctions[{renderSummary.junctions}] markers[{renderSummary.markers}]
          </span>
        ) : null}
        {debugEnabled ? (
          <span>
            page[{Math.round(activePage.bounds.x)},{Math.round(activePage.bounds.y)},{Math.round(activePage.bounds.width)},{Math.round(activePage.bounds.height)}]
            {" "}content[
            {activePage.contentBounds
              ? `${Math.round(activePage.contentBounds.x)},${Math.round(activePage.contentBounds.y)},${Math.round(activePage.contentBounds.width)},${Math.round(activePage.contentBounds.height)}`
              : "none"}
            ]
          </span>
        ) : null}
      </div>
    </section>
  );
}

function DebugScreenGrid({ width, height }: { width: number; height: number }) {
  const majorStep = 100;
  const minorStep = 20;
  const verticalMinor = Array.from({ length: Math.ceil(width / minorStep) }, (_, index) => index * minorStep);
  const horizontalMinor = Array.from({ length: Math.ceil(height / minorStep) }, (_, index) => index * minorStep);
  const verticalMajor = Array.from({ length: Math.ceil(width / majorStep) }, (_, index) => index * majorStep);
  const horizontalMajor = Array.from({ length: Math.ceil(height / majorStep) }, (_, index) => index * majorStep);

  return (
    <g className="schematic-debug-screen">
      {verticalMinor.map((x) => (
        <line key={`minor-v-${x}`} x1={x} y1={0} x2={x} y2={height} stroke="#cbd5e1" strokeWidth={0.5} />
      ))}
      {horizontalMinor.map((y) => (
        <line key={`minor-h-${y}`} x1={0} y1={y} x2={width} y2={y} stroke="#cbd5e1" strokeWidth={0.5} />
      ))}
      {verticalMajor.map((x) => (
        <g key={`major-v-${x}`}>
          <line x1={x} y1={0} x2={x} y2={height} stroke="#64748b" strokeWidth={0.8} />
          <text x={x + 4} y={14} className="schematic-debug-label" fontSize={SCHEMATIC_TEXT.debugLabel}>
            {x}
          </text>
        </g>
      ))}
      {horizontalMajor.map((y) => (
        <g key={`major-h-${y}`}>
          <line x1={0} y1={y} x2={width} y2={y} stroke="#64748b" strokeWidth={0.8} />
          <text x={4} y={y - 4} className="schematic-debug-label" fontSize={SCHEMATIC_TEXT.debugLabel}>
            {y}
          </text>
        </g>
      ))}
      <line x1={0} y1={0} x2={70} y2={0} stroke="#dc2626" strokeWidth={1.2} />
      <line x1={0} y1={0} x2={0} y2={70} stroke="#2563eb" strokeWidth={1.2} />
      <text x={6} y={84} className="schematic-debug-label" fontSize={SCHEMATIC_TEXT.debugLabel}>origin</text>
    </g>
  );
}

function LocatorCircle() {
  const centerX = su(12);
  const centerY = su(12);
  const radius = su(3);

  return (
    <g className="schematic-locator-circle">
      <circle cx={centerX} cy={centerY} r={radius} fill="none" stroke="#dc2626" strokeWidth={SCHEMATIC_STROKE.overlay} />
      <line x1={centerX - radius - su(1)} y1={centerY} x2={centerX + radius + su(1)} y2={centerY} stroke="#dc2626" strokeWidth={SCHEMATIC_STROKE.debug} />
      <line x1={centerX} y1={centerY - radius - su(1)} x2={centerX} y2={centerY + radius + su(1)} stroke="#dc2626" strokeWidth={SCHEMATIC_STROKE.debug} />
      <text x={centerX + su(4)} y={centerY + su(0.5)} fill="#dc2626" fontSize={SCHEMATIC_TEXT.debugFixture}>
        LOCATOR
      </text>
    </g>
  );
}

function DiagnosticFixture() {
  return (
    <g className="schematic-diagnostic-fixture">
      <rect x={1040} y={120} width={160} height={90} fill="none" stroke="#dc2626" strokeWidth={1.2} vectorEffect="non-scaling-stroke" />
      <line x1={1000} y1={150} x2={1040} y2={150} stroke="#dc2626" strokeWidth={1.2} vectorEffect="non-scaling-stroke" />
      <line x1={1200} y1={180} x2={1240} y2={180} stroke="#dc2626" strokeWidth={1.2} vectorEffect="non-scaling-stroke" />
      <polyline points="1240,180 1300,180 1300,240 1360,240" fill="none" stroke="#dc2626" strokeWidth={1.2} vectorEffect="non-scaling-stroke" />
      <text x={1050} y={110} className="schematic-debug-fixture" fontSize={SCHEMATIC_TEXT.debugFixture}>DBG-U1</text>
      <text x={1062} y={164} className="schematic-debug-fixture" fontSize={SCHEMATIC_TEXT.debugFixture}>Debug Fixture</text>
    </g>
  );
}

function DebugOverlay({ page }: { page: SchematicPageScene }) {
  return (
    <g className="schematic-debug-overlay">
      <rect
        x={page.bounds.x}
        y={page.bounds.y}
        width={page.bounds.width}
        height={page.bounds.height}
        fill="none"
        stroke="#2563eb"
        strokeWidth={2}
        vectorEffect="non-scaling-stroke"
      />
      {page.contentBounds ? (
        <rect
          x={page.contentBounds.x}
          y={page.contentBounds.y}
          width={page.contentBounds.width}
          height={page.contentBounds.height}
          fill="none"
          stroke="#dc2626"
          strokeWidth={2}
          strokeDasharray="10 6"
          vectorEffect="non-scaling-stroke"
        />
      ) : null}
      {page.instances.map((instance) => (
        <g key={`debug-${instance.instanceId}`}>
          <rect
            x={instance.bounds.x}
            y={instance.bounds.y}
            width={instance.bounds.width}
            height={instance.bounds.height}
            fill="none"
            stroke="#16a34a"
            strokeWidth={1.4}
            strokeDasharray="6 4"
            vectorEffect="non-scaling-stroke"
          />
          <text x={instance.bounds.x + 4} y={instance.bounds.y - 4} className="schematic-debug-label" fontSize={SCHEMATIC_TEXT.debugLabel}>
            {instance.instanceId}
          </text>
        </g>
      ))}
    </g>
  );
}

function PageFrame({ page }: { page: SchematicPageScene }) {
  const titleBoxWidth = SCHEMATIC_TITLE_BOX.width;
  const titleBoxHeight = SCHEMATIC_TITLE_BOX.height;
  const titleBoxX = page.size.width - titleBoxWidth - SCHEMATIC_TITLE_BOX.rightInset;
  const titleBoxY = page.size.height - titleBoxHeight - SCHEMATIC_TITLE_BOX.bottomInset;

  return (
    <g className="schematic-layer-frame">
      <rect
        x={SCHEMATIC_PAGE_FRAME_INSET}
        y={SCHEMATIC_PAGE_FRAME_INSET}
        width={page.size.width - SCHEMATIC_PAGE_FRAME_INSET * 2}
        height={page.size.height - SCHEMATIC_PAGE_FRAME_INSET * 2}
        fill="none"
        stroke="#9ca3af"
        strokeWidth={SCHEMATIC_STROKE.frame}
      />
      <rect x={titleBoxX} y={titleBoxY} width={titleBoxWidth} height={titleBoxHeight} fill="none" stroke="#6b7280" strokeWidth={SCHEMATIC_STROKE.frame} />
      <line x1={titleBoxX} y1={titleBoxY + SCHEMATIC_TITLE_BOX.headerHeight} x2={titleBoxX + titleBoxWidth} y2={titleBoxY + SCHEMATIC_TITLE_BOX.headerHeight} stroke="#6b7280" strokeWidth={SCHEMATIC_STROKE.frame} />
      <line x1={titleBoxX + SCHEMATIC_TITLE_BOX.sectionWidth} y1={titleBoxY + SCHEMATIC_TITLE_BOX.headerHeight} x2={titleBoxX + SCHEMATIC_TITLE_BOX.sectionWidth} y2={titleBoxY + titleBoxHeight} stroke="#6b7280" strokeWidth={SCHEMATIC_STROKE.frame} />
      <text className="schematic-title" x={su(2.5)} y={su(3.25)} fontSize={SCHEMATIC_TEXT.title}>
        {page.title}
      </text>
      <text className="schematic-sheet-meta" x={titleBoxX + su(0.75)} y={titleBoxY + su(1.125)} fontSize={SCHEMATIC_TEXT.sheetMeta}>
        TITLE
      </text>
      <text className="schematic-sheet-value" x={titleBoxX + su(0.75)} y={titleBoxY + su(3.25)} fontSize={SCHEMATIC_TEXT.sheetValue}>
        {page.title}
      </text>
      <text className="schematic-sheet-meta" x={titleBoxX + SCHEMATIC_TITLE_BOX.sectionWidth + su(0.75)} y={titleBoxY + su(1.125)} fontSize={SCHEMATIC_TEXT.sheetMeta}>
        SHEET
      </text>
      <text className="schematic-sheet-value" x={titleBoxX + SCHEMATIC_TITLE_BOX.sectionWidth + su(0.75)} y={titleBoxY + su(3.25)} fontSize={SCHEMATIC_TEXT.sheetValue}>
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
          strokeWidth={wire.style === "clock" ? SCHEMATIC_STROKE.clockWire : SCHEMATIC_STROKE.wire}
          strokeLinejoin="miter"
          strokeLinecap="square"
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
          r={SCHEMATIC_RADIUS.junction}
          fill="#111827"
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
          <text className="schematic-refdes" x={instance.refdesPosition.x} y={instance.refdesPosition.y} fontSize={SCHEMATIC_TEXT.refdes}>
            {instance.refdes}
          </text>
          <text className="schematic-value" x={instance.valuePosition.x} y={instance.valuePosition.y} fontSize={SCHEMATIC_TEXT.value}>
            {instance.value}
          </text>
          {instance.placeholderMessage ? (
            <text className="schematic-placeholder-message" x={instance.bounds.x + su(0.5)} y={instance.bounds.y + instance.bounds.height + su(2)} fontSize={SCHEMATIC_TEXT.placeholder}>
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
          fontSize={SCHEMATIC_TEXT.netLabel}
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
          <circle r={SCHEMATIC_RADIUS.marker} fill="#f59e0b" stroke="#78350f" strokeWidth={SCHEMATIC_STROKE.marker} />
          <text className="schematic-marker-text" x={0} y={su(0.175)} textAnchor="middle" fontSize={SCHEMATIC_TEXT.marker}>
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
      <text className="schematic-pin-name" x={pin.labelPosition.x} y={pin.labelPosition.y} textAnchor={pin.labelAnchor} fontSize={SCHEMATIC_TEXT.pinName}>
        {pin.name}
      </text>
      <text className="schematic-pin-number" x={pin.numberPosition.x} y={pin.numberPosition.y} textAnchor={pin.numberAnchor} fontSize={SCHEMATIC_TEXT.pinNumber}>
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
          strokeWidth={primitive.strokeWidth ?? SCHEMATIC_STROKE.symbol}
          strokeLinecap="square"
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
          strokeWidth={primitive.strokeWidth ?? SCHEMATIC_STROKE.symbol}
          strokeLinecap="square"
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
          strokeWidth={primitive.strokeWidth ?? SCHEMATIC_STROKE.symbol}
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
          strokeWidth={primitive.strokeWidth ?? SCHEMATIC_STROKE.symbol}
        />
      );
    case "polyline":
      return (
        <polyline
          points={primitive.points.map((point) => `${point.x},${point.y}`).join(" ")}
          fill={primitive.fill ?? "none"}
          stroke={normalizeStrokeColor(primitive.stroke)}
          strokeWidth={primitive.strokeWidth ?? SCHEMATIC_STROKE.symbol}
          strokeLinejoin="miter"
          strokeLinecap="square"
        />
      );
    case "text":
      return (
        <text
          x={primitive.position.x}
          y={primitive.position.y}
          fontSize={primitive.fontSize ?? SCHEMATIC_TEXT.primitiveBody}
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
