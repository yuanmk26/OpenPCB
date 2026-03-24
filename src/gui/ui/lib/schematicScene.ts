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
  const safeWidth = Math.max(containerSize.width, 1);
  const safeHeight = Math.max(containerSize.height, 1);
  const padding = 36;
  const scale = Math.min(
    (safeWidth - padding * 2) / pageSize.width,
    (safeHeight - padding * 2) / pageSize.height
  );
  const normalizedScale = Number.isFinite(scale) && scale > 0 ? scale : 1;

  return {
    scale: normalizedScale,
    pan: {
      x: (safeWidth - pageSize.width * normalizedScale) / 2,
      y: (safeHeight - pageSize.height * normalizedScale) / 2
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

  return {
    pageId: page.pageId,
    title: page.title,
    size: page.size,
    bounds: { x: 0, y: 0, width: page.size.width, height: page.size.height },
    instances,
    wires: page.wires.map((wire) => ({
      ...wire,
      bounds: wire.bounds ?? boundsFromPoints(wire.points)
    })),
    labels: page.labels.map((label) => ({
      ...label,
      bounds: label.bounds ?? {
        x: label.position.x,
        y: label.position.y - 14,
        width: label.text.length * 9,
        height: 18
      }
    })),
    junctions: page.junctions.map((junction) => ({
      ...junction,
      bounds: junction.bounds ?? {
        x: junction.position.x - 4,
        y: junction.position.y - 4,
        width: 8,
        height: 8
      }
    })),
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
    { x: symbol.bounds.x + 6, y: symbol.bounds.y - 10 },
    instance.position,
    instance.rotation,
    instance.mirror
  );
  const defaultValuePosition = transformPoint(
    { x: symbol.bounds.x + 6, y: symbol.bounds.y + symbol.bounds.height + 18 },
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
    bounds: { x: 0, y: 0, width: 160, height: 90 },
    pins: [],
    graphics: [
      { id: "body", type: "rect", origin: { x: 0, y: 0 }, width: 160, height: 90, stroke: "#111827", strokeWidth: 1.5 },
      { id: "diag-a", type: "line", start: { x: 0, y: 0 }, end: { x: 160, y: 90 }, stroke: "#9f1239", strokeWidth: 1.2 },
      { id: "diag-b", type: "line", start: { x: 160, y: 0 }, end: { x: 0, y: 90 }, stroke: "#9f1239", strokeWidth: 1.2 },
      { id: "txt", type: "text", position: { x: 80, y: 46 }, text: "MISSING SYMBOL", anchor: "middle", fontSize: 12 }
    ]
  };
  const bounds = boundsFromPoints([
    transformPoint({ x: 0, y: 0 }, instance.position, instance.rotation, instance.mirror),
    transformPoint({ x: 160, y: 0 }, instance.position, instance.rotation, instance.mirror),
    transformPoint({ x: 160, y: 90 }, instance.position, instance.rotation, instance.mirror),
    transformPoint({ x: 0, y: 90 }, instance.position, instance.rotation, instance.mirror)
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
    refdesPosition: { x: bounds.x + 8, y: bounds.y - 10 },
    valuePosition: { x: bounds.x + 8, y: bounds.y + bounds.height + 18 },
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
        labelPosition: { x: anchor.x + 8, y: anchor.y - 4 },
        numberPosition: { x: anchor.x - 8, y: anchor.y - 4 },
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
        labelPosition: { x: anchor.x - 8, y: anchor.y - 4 },
        numberPosition: { x: anchor.x + 8, y: anchor.y - 4 },
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
        labelPosition: { x: anchor.x, y: anchor.y + 18 },
        numberPosition: { x: anchor.x, y: anchor.y - 10 },
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
        labelPosition: { x: anchor.x, y: anchor.y - 10 },
        numberPosition: { x: anchor.x, y: anchor.y + 20 },
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
        y: primitive.position.y - (primitive.fontSize ?? 14),
        width: primitive.text.length * ((primitive.fontSize ?? 14) * 0.62),
        height: primitive.fontSize ?? 14
      };
  }
}
