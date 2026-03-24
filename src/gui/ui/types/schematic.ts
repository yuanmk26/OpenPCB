export type Point = {
  x: number;
  y: number;
};

export type Bounds = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type PageSize = {
  width: number;
  height: number;
};

export type Rotation = 0 | 90 | 180 | 270;

export type SymbolPinDirection = "left" | "right" | "up" | "down";

export type NetStyle = "signal" | "power" | "ground" | "clock";

export type MarkerKind = "info" | "warning" | "error";

type GraphicBase = {
  id: string;
  stroke?: string;
  strokeWidth?: number;
};

export type LineGraphic = GraphicBase & {
  type: "line";
  start: Point;
  end: Point;
};

export type RectGraphic = GraphicBase & {
  type: "rect";
  origin: Point;
  width: number;
  height: number;
  fill?: string;
};

export type CircleGraphic = GraphicBase & {
  type: "circle";
  center: Point;
  radius: number;
  fill?: string;
};

export type PolylineGraphic = GraphicBase & {
  type: "polyline";
  points: Point[];
  closed?: boolean;
  fill?: string;
};

export type TextGraphic = GraphicBase & {
  type: "text";
  position: Point;
  text: string;
  fontSize?: number;
  anchor?: "start" | "middle" | "end";
};

export type PinStubGraphic = GraphicBase & {
  type: "pin_stub";
  start: Point;
  end: Point;
};

export type GraphicPrimitive =
  | LineGraphic
  | RectGraphic
  | CircleGraphic
  | PolylineGraphic
  | TextGraphic
  | PinStubGraphic;

export type SymbolPin = {
  pinId: string;
  number: string;
  name: string;
  anchor: Point;
  direction: SymbolPinDirection;
};

export type SymbolDefinition = {
  symbolId: string;
  name: string;
  pins: SymbolPin[];
  graphics: GraphicPrimitive[];
  bounds: Bounds;
};

export type PlacedInstance = {
  instanceId: string;
  symbolId: string;
  refdes: string;
  value: string;
  position: Point;
  rotation: Rotation;
  mirror: boolean;
  refdesPosition?: Point;
  valuePosition?: Point;
  pinAnchorOverrides?: Record<string, Point>;
  bounds?: Bounds;
};

export type WireSegment = {
  wireId: string;
  netId: string;
  points: Point[];
  style: NetStyle;
  bounds?: Bounds;
};

export type NetLabel = {
  labelId: string;
  netId: string;
  text: string;
  position: Point;
  orientation: Rotation;
  bounds?: Bounds;
};

export type Junction = {
  junctionId: string;
  position: Point;
  bounds?: Bounds;
};

export type Marker = {
  markerId: string;
  kind: MarkerKind;
  position: Point;
  message: string;
};

export type GeometryPage = {
  pageId: string;
  title: string;
  size: PageSize;
  instances: PlacedInstance[];
  wires: WireSegment[];
  labels: NetLabel[];
  junctions: Junction[];
  markers: Marker[];
};

export type SchematicNet = {
  netId: string;
  name: string;
  style: NetStyle;
};

export type SchematicGeometry = {
  version: string;
  symbolLibrary: Record<string, SymbolDefinition>;
  pages: GeometryPage[];
  nets: SchematicNet[];
  metadata: Record<string, string>;
};

export type ResolvedInstance = {
  instanceId: string;
  symbolId: string;
  refdes: string;
  value: string;
  bounds: Bounds;
  transform: string;
  symbol: SymbolDefinition;
  globalPins: Record<string, Point>;
  renderedPins: ResolvedPin[];
  refdesPosition: Point;
  valuePosition: Point;
  isPlaceholder?: boolean;
  placeholderMessage?: string;
};

export type ResolvedPin = {
  pinId: string;
  number: string;
  name: string;
  anchor: Point;
  direction: SymbolPinDirection;
  labelPosition: Point;
  numberPosition: Point;
  labelAnchor: "start" | "middle" | "end";
  numberAnchor: "start" | "middle" | "end";
};

export type SchematicPageScene = {
  pageId: string;
  title: string;
  size: PageSize;
  bounds: Bounds;
  contentBounds: Bounds | null;
  instances: ResolvedInstance[];
  wires: WireSegment[];
  labels: NetLabel[];
  junctions: Junction[];
  markers: Marker[];
};

export type SchematicScene = {
  version: string;
  pages: SchematicPageScene[];
  nets: SchematicNet[];
  metadata: Record<string, string>;
};

export type ViewportState = {
  pageId: string;
  scale: number;
  pan: Point;
};
