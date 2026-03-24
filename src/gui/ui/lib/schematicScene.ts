import type {
  Bounds,
  GeometryPage,
  GraphicPrimitive,
  PageSize,
  PlacedInstance,
  Point,
  ResolvedPin,
  ResolvedInstance,
  Rotation,
  SchematicGeometry,
  SchematicPageScene,
  SchematicScene,
  SymbolDefinition
} from "@/types/schematic";
import {
  SCHEMATIC_CONTENT_BOUNDS_MARGIN,
  SCHEMATIC_STROKE,
  SCHEMATIC_TEXT,
  SCHEMATIC_VIEWPORT_CONTENT_EDGE_PADDING,
  SCHEMATIC_VIEWPORT_CONTENT_PADDING,
  SCHEMATIC_VIEWPORT_PAGE_PADDING,
  su
} from "@/lib/schematicMetrics";

export function buildSchematicScene(geometry: SchematicGeometry): SchematicScene {
  return {
    version: geometry.version,
    metadata: geometry.metadata,
    nets: geometry.nets,
    pages: geometry.pages.map((page) => buildPageScene(page, geometry.symbolLibrary))
  };
}

export function getPageScene(
  scene: SchematicScene,
  pageId: string
): SchematicPageScene | undefined {
  return scene.pages.find((page) => page.pageId === pageId);
}

export function fitViewport(
  pageSize: PageSize,
  containerSize: { width: number; height: number }
): { scale: number; pan: Point } {
  return fitViewportToPage({ x: 0, y: 0, width: pageSize.width, height: pageSize.height }, containerSize);
}

export function fitViewportToPage(
  pageBounds: Bounds,
  containerSize: { width: number; height: number },
): { scale: number; pan: Point } {
  const safeWidth = Math.max(containerSize.width, 1);
  const safeHeight = Math.max(containerSize.height, 1);
  const padding = SCHEMATIC_VIEWPORT_PAGE_PADDING;
  const targetWidth = Math.max(pageBounds.width, 1);
  const targetHeight = Math.max(pageBounds.height, 1);
  const availableWidth = Math.max(safeWidth - padding * 2, 1);
  const availableHeight = Math.max(safeHeight - padding * 2, 1);
  const scale = Math.min(
    availableWidth / targetWidth,
    availableHeight / targetHeight
  );
  const normalizedScale = Number.isFinite(scale) && scale > 0 ? scale : 1;
  const scaledWidth = pageBounds.width * normalizedScale;
  const scaledHeight = pageBounds.height * normalizedScale;

  return {
    scale: normalizedScale,
    pan: {
      x: (safeWidth - scaledWidth) / 2 - pageBounds.x * normalizedScale,
      y: (safeHeight - scaledHeight) / 2 - pageBounds.y * normalizedScale
    }
  };
}

export function fitViewportToContent(
  contentBounds: Bounds,
  pageBounds: Bounds,
  containerSize: { width: number; height: number }
): { scale: number; pan: Point } {
  const safeWidth = Math.max(containerSize.width, 1);
  const safeHeight = Math.max(containerSize.height, 1);
  const contentPadding = SCHEMATIC_VIEWPORT_CONTENT_PADDING;
  const pagePadding = SCHEMATIC_VIEWPORT_CONTENT_EDGE_PADDING;
  const availableContentWidth = Math.max(safeWidth - contentPadding * 2, 1);
  const availableContentHeight = Math.max(safeHeight - contentPadding * 2, 1);
  const availablePageWidth = Math.max(safeWidth - pagePadding * 2, 1);
  const availablePageHeight = Math.max(safeHeight - pagePadding * 2, 1);
  const contentScale = Math.min(
    availableContentWidth / Math.max(contentBounds.width, 1),
    availableContentHeight / Math.max(contentBounds.height, 1)
  );
  const pageScale = Math.min(
    availablePageWidth / Math.max(pageBounds.width, 1),
    availablePageHeight / Math.max(pageBounds.height, 1)
  );
  const scale = Math.min(contentScale, pageScale);
  const normalizedScale = Number.isFinite(scale) && scale > 0 ? scale : 1;
  const targetPaperMinX = pagePadding;
  const targetPaperMinY = pagePadding;
  const targetPaperMaxX = safeWidth - pagePadding - pageBounds.width * normalizedScale;
  const targetPaperMaxY = safeHeight - pagePadding - pageBounds.height * normalizedScale;
  const contentCenterX = (contentBounds.x + contentBounds.width / 2) * normalizedScale;
  const contentCenterY = (contentBounds.y + contentBounds.height / 2) * normalizedScale;
  const desiredPanX = safeWidth / 2 - contentCenterX;
  const desiredPanY = safeHeight / 2 - contentCenterY;

  return {
    scale: normalizedScale,
    pan: {
      x: clamp(desiredPanX, targetPaperMaxX, targetPaperMinX),
      y: clamp(desiredPanY, targetPaperMaxY, targetPaperMinY)
    }
  };
}

function buildPageScene(
  page: GeometryPage,
  symbolLibrary: Record<string, SymbolDefinition>
): SchematicPageScene {
  const markerBuffer = [...page.markers];
  const instances = page.instances.flatMap((instance) => {
    const symbol = symbolLibrary[instance.symbolId];

    if (!symbol) {
      return [buildPlaceholderInstance(instance, markerBuffer)];
    }

    return [resolveInstance(instance, symbol)];
  });
  const wires = page.wires.map((wire) => ({
    ...wire,
    bounds: wire.bounds ?? boundsFromPoints(wire.points)
  }));
  const labels = page.labels.map((label) => ({
    ...label,
    bounds: label.bounds ?? {
      x: label.position.x,
      y: label.position.y - SCHEMATIC_TEXT.netLabel,
      width: label.text.length * (SCHEMATIC_TEXT.netLabel * 0.72),
      height: SCHEMATIC_TEXT.netLabel
    }
  }));
  const junctions = page.junctions.map((junction) => ({
    ...junction,
    bounds: junction.bounds ?? {
      x: junction.position.x - su(0.25),
      y: junction.position.y - su(0.25),
      width: su(0.5),
      height: su(0.5)
    }
  }));
  const contentBounds = mergeBounds([
    ...instances.map((instance) => instance.bounds),
    ...wires.map((wire) => wire.bounds).filter(Boolean),
    ...labels.map((label) => label.bounds).filter(Boolean),
    ...junctions.map((junction) => junction.bounds).filter(Boolean)
  ]);

  return {
    pageId: page.pageId,
    title: page.title,
    size: page.size,
    bounds: { x: 0, y: 0, width: page.size.width, height: page.size.height },
    contentBounds,
    instances,
    wires,
    labels,
    junctions,
    markers: markerBuffer
  };
}

function resolveInstance(
  instance: PlacedInstance,
  symbol: SymbolDefinition
): ResolvedInstance {
  const corners = [
    { x: symbol.bounds.x, y: symbol.bounds.y },
    { x: symbol.bounds.x + symbol.bounds.width, y: symbol.bounds.y },
    { x: symbol.bounds.x + symbol.bounds.width, y: symbol.bounds.y + symbol.bounds.height },
    { x: symbol.bounds.x, y: symbol.bounds.y + symbol.bounds.height }
  ].map((point) => transformPoint(point, instance.position, instance.rotation, instance.mirror));

  const bounds = boundsFromPoints(corners);
  const globalPins = Object.fromEntries(
    symbol.pins.map((pin) => {
      const override = instance.pinAnchorOverrides?.[pin.pinId];
      const localAnchor = override ?? pin.anchor;
      const anchor = transformPoint(localAnchor, instance.position, instance.rotation, instance.mirror);
      return [pin.pinId, anchor];
    })
  );
  const renderedPins = symbol.pins.map((pin) =>
    buildRenderedPin(pin.number, pin.name, pin.pinId, pin.direction, globalPins[pin.pinId])
  );

  const defaultRefdesPosition = transformPoint(
    { x: symbol.bounds.x + su(0.375), y: symbol.bounds.y - su(0.625) },
    instance.position,
    instance.rotation,
    instance.mirror
  );
  const defaultValuePosition = transformPoint(
    { x: symbol.bounds.x + su(0.375), y: symbol.bounds.y + symbol.bounds.height + su(1.125) },
    instance.position,
    instance.rotation,
    instance.mirror
  );

  return {
    instanceId: instance.instanceId,
    symbolId: instance.symbolId,
    refdes: instance.refdes,
    value: instance.value,
    bounds: instance.bounds ?? bounds,
    transform: buildInstanceTransform(instance.position, instance.rotation, instance.mirror),
    symbol,
    globalPins,
    renderedPins,
    refdesPosition: instance.refdesPosition ?? defaultRefdesPosition,
    valuePosition: instance.valuePosition ?? defaultValuePosition
  };
}

function buildPlaceholderInstance(
  instance: PlacedInstance,
  markerBuffer: SchematicPageScene["markers"]
): ResolvedInstance {
  const placeholderSymbol: SymbolDefinition = {
    symbolId: "missing-symbol-placeholder",
    name: "Missing Symbol",
    bounds: { x: 0, y: 0, width: su(10), height: su(6) },
    pins: [],
    graphics: [
      { id: "body", type: "rect", origin: { x: 0, y: 0 }, width: su(10), height: su(6), stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbolStrong },
      { id: "diag-a", type: "line", start: { x: 0, y: 0 }, end: { x: su(10), y: su(6) }, stroke: "#9f1239", strokeWidth: SCHEMATIC_STROKE.symbol },
      { id: "diag-b", type: "line", start: { x: su(10), y: 0 }, end: { x: 0, y: su(6) }, stroke: "#9f1239", strokeWidth: SCHEMATIC_STROKE.symbol },
      { id: "txt", type: "text", position: { x: su(5), y: su(3.125) }, text: "MISSING SYMBOL", anchor: "middle", fontSize: SCHEMATIC_TEXT.primitiveSmall }
    ]
  };
  const bounds = boundsFromPoints([
    transformPoint({ x: 0, y: 0 }, instance.position, instance.rotation, instance.mirror),
    transformPoint({ x: su(10), y: 0 }, instance.position, instance.rotation, instance.mirror),
    transformPoint({ x: su(10), y: su(6) }, instance.position, instance.rotation, instance.mirror),
    transformPoint({ x: 0, y: su(6) }, instance.position, instance.rotation, instance.mirror)
  ]);

  markerBuffer.push({
    markerId: `missing-symbol:${instance.instanceId}`,
    kind: "error",
    position: instance.position,
    message: `Missing symbol definition: ${instance.symbolId}`
  });

  return {
    instanceId: instance.instanceId,
    symbolId: instance.symbolId,
    refdes: instance.refdes,
    value: instance.value,
    bounds,
    transform: buildInstanceTransform(instance.position, instance.rotation, instance.mirror),
    symbol: placeholderSymbol,
    globalPins: {},
    renderedPins: [],
    refdesPosition: { x: bounds.x + su(0.5), y: bounds.y - su(0.625) },
    valuePosition: { x: bounds.x + su(0.5), y: bounds.y + bounds.height + su(1.125) },
    isPlaceholder: true,
    placeholderMessage: `Missing symbol: ${instance.symbolId}`
  };
}

function buildRenderedPin(
  number: string,
  name: string,
  pinId: string,
  direction: ResolvedPin["direction"],
  anchor: Point
): ResolvedPin {
  switch (direction) {
    case "left":
      return {
        pinId,
        number,
        name,
        anchor,
        direction,
        labelPosition: { x: anchor.x + su(0.5), y: anchor.y - su(0.25) },
        numberPosition: { x: anchor.x - su(0.5), y: anchor.y - su(0.25) },
        labelAnchor: "start",
        numberAnchor: "end"
      };
    case "right":
      return {
        pinId,
        number,
        name,
        anchor,
        direction,
        labelPosition: { x: anchor.x - su(0.5), y: anchor.y - su(0.25) },
        numberPosition: { x: anchor.x + su(0.5), y: anchor.y - su(0.25) },
        labelAnchor: "end",
        numberAnchor: "start"
      };
    case "up":
      return {
        pinId,
        number,
        name,
        anchor,
        direction,
        labelPosition: { x: anchor.x, y: anchor.y + su(1.125) },
        numberPosition: { x: anchor.x, y: anchor.y - su(0.625) },
        labelAnchor: "middle",
        numberAnchor: "middle"
      };
    case "down":
      return {
        pinId,
        number,
        name,
        anchor,
        direction,
        labelPosition: { x: anchor.x, y: anchor.y - su(0.625) },
        numberPosition: { x: anchor.x, y: anchor.y + su(1.25) },
        labelAnchor: "middle",
        numberAnchor: "middle"
      };
  }
}

function buildInstanceTransform(position: Point, rotation: Rotation, mirror: boolean): string {
  const commands = [`translate(${position.x} ${position.y})`];

  if (rotation !== 0) {
    commands.push(`rotate(${rotation})`);
  }

  if (mirror) {
    commands.push("scale(-1 1)");
  }

  return commands.join(" ");
}

function transformPoint(
  point: Point,
  position: Point,
  rotation: Rotation,
  mirror: boolean
): Point {
  let next = { ...point };

  if (mirror) {
    next = { x: -next.x, y: next.y };
  }

  switch (rotation) {
    case 90:
      next = { x: -next.y, y: next.x };
      break;
    case 180:
      next = { x: -next.x, y: -next.y };
      break;
    case 270:
      next = { x: next.y, y: -next.x };
      break;
    default:
      break;
  }

  return {
    x: next.x + position.x,
    y: next.y + position.y
  };
}

function boundsFromPoints(points: Point[]): Bounds {
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);

  return {
    x: Math.min(...xs),
    y: Math.min(...ys),
    width: Math.max(...xs) - Math.min(...xs),
    height: Math.max(...ys) - Math.min(...ys)
  };
}

export function getPrimitiveBounds(primitive: GraphicPrimitive): Bounds {
  switch (primitive.type) {
    case "line":
      return boundsFromPoints([primitive.start, primitive.end]);
    case "pin_stub":
      return boundsFromPoints([primitive.start, primitive.end]);
    case "rect":
      return {
        x: primitive.origin.x,
        y: primitive.origin.y,
        width: primitive.width,
        height: primitive.height
      };
    case "circle":
      return {
        x: primitive.center.x - primitive.radius,
        y: primitive.center.y - primitive.radius,
        width: primitive.radius * 2,
        height: primitive.radius * 2
      };
    case "polyline":
      return boundsFromPoints(primitive.points);
    case "text":
      return {
        x: primitive.position.x,
        y: primitive.position.y - (primitive.fontSize ?? SCHEMATIC_TEXT.primitiveBody),
        width: primitive.text.length * ((primitive.fontSize ?? SCHEMATIC_TEXT.primitiveBody) * 0.62),
        height: primitive.fontSize ?? SCHEMATIC_TEXT.primitiveBody
      };
  }
}

function mergeBounds(boundsList: Array<Bounds | undefined>): Bounds | null {
  const filtered = boundsList.filter((item): item is Bounds => Boolean(item));

  if (filtered.length === 0) {
    return null;
  }

  const minX = Math.min(...filtered.map((bounds) => bounds.x));
  const minY = Math.min(...filtered.map((bounds) => bounds.y));
  const maxX = Math.max(...filtered.map((bounds) => bounds.x + bounds.width));
  const maxY = Math.max(...filtered.map((bounds) => bounds.y + bounds.height));

  return {
    x: minX - SCHEMATIC_CONTENT_BOUNDS_MARGIN,
    y: minY - SCHEMATIC_CONTENT_BOUNDS_MARGIN,
    width: maxX - minX + SCHEMATIC_CONTENT_BOUNDS_MARGIN * 2,
    height: maxY - minY + SCHEMATIC_CONTENT_BOUNDS_MARGIN * 2
  };
}

function clamp(value: number, minValue: number, maxValue: number): number {
  return Math.min(Math.max(value, minValue), maxValue);
}
