export const SCHEMATIC_UNIT = 16;

export function su(value: number): number {
  return Math.round(value * SCHEMATIC_UNIT);
}

export const SCHEMATIC_VIEWPORT_PAGE_PADDING = su(3);
export const SCHEMATIC_VIEWPORT_CONTENT_PADDING = su(4);
export const SCHEMATIC_VIEWPORT_CONTENT_EDGE_PADDING = su(2);
export const SCHEMATIC_CONTENT_BOUNDS_MARGIN = su(2.5);

export const SCHEMATIC_PAGE_GRID_STEP = su(4);
export const SCHEMATIC_PAGE_FRAME_INSET = su(1.5);
export const SCHEMATIC_PAGE_INNER_INSET = su(1.25);
export const SCHEMATIC_TITLE_BOX = {
  width: su(21),
  height: su(6),
  sectionWidth: su(6),
  headerHeight: su(1.75),
  rightInset: su(1.75),
  bottomInset: su(1.5)
};

export const SCHEMATIC_STROKE = {
  pageBorder: 1,
  frame: 0.8,
  wire: 1.2,
  clockWire: 1.6,
  symbol: 1.2,
  symbolStrong: 1.4,
  marker: 0.8,
  debug: 1.2,
  overlay: 2
};

export const SCHEMATIC_TEXT = {
  primitiveSmall: su(0.875),
  primitiveBody: su(1),
  primitiveTitle: su(1.125),
  refdes: su(0.75),
  value: su(0.75),
  netLabel: su(0.75),
  title: su(1.125),
  sheetMeta: su(0.5625),
  sheetValue: su(0.75),
  pinName: su(0.625),
  pinNumber: su(0.5625),
  placeholder: su(0.625),
  marker: su(0.625),
  debugLabel: su(0.625),
  debugFixture: su(0.6875)
};

export const SCHEMATIC_RADIUS = {
  junction: su(0.2),
  marker: su(0.375)
};
