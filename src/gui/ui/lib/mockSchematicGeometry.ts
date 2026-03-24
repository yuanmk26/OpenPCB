import { SCHEMATIC_STROKE, SCHEMATIC_TEXT, su } from "@/lib/schematicMetrics";
import type { SchematicGeometry } from "@/types/schematic";

const u = su;

export const mockSchematicGeometry: SchematicGeometry = {
  version: "1.0.0",
  symbolLibrary: {
    "usb-c-input": {
      symbolId: "usb-c-input",
      name: "USB-C Input",
      bounds: { x: 0, y: 0, width: u(8), height: u(6) },
      pins: [
        { pinId: "vbus", number: "A4", name: "VBUS", anchor: { x: u(8), y: u(1.5) }, direction: "right" },
        { pinId: "gnd", number: "A1", name: "GND", anchor: { x: u(8), y: u(4.5) }, direction: "right" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: u(1), y: u(1) }, width: u(6), height: u(4), stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "p1", type: "pin_stub", start: { x: u(7), y: u(1.5) }, end: { x: u(8), y: u(1.5) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "p2", type: "pin_stub", start: { x: u(7), y: u(4.5) }, end: { x: u(8), y: u(4.5) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "t1", type: "text", position: { x: u(4), y: u(3) }, text: "USB-C", anchor: "middle", fontSize: SCHEMATIC_TEXT.primitiveBody }
      ]
    },
    ldo: {
      symbolId: "ldo",
      name: "LDO Regulator",
      bounds: { x: 0, y: 0, width: u(10), height: u(7) },
      pins: [
        { pinId: "vin", number: "1", name: "VIN", anchor: { x: 0, y: u(2) }, direction: "left" },
        { pinId: "gnd", number: "2", name: "GND", anchor: { x: u(5), y: u(7) }, direction: "down" },
        { pinId: "vout", number: "3", name: "VOUT", anchor: { x: u(10), y: u(2) }, direction: "right" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: u(2), y: u(1) }, width: u(6), height: u(4.5), stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "vin", type: "pin_stub", start: { x: 0, y: u(2) }, end: { x: u(2), y: u(2) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "vout", type: "pin_stub", start: { x: u(8), y: u(2) }, end: { x: u(10), y: u(2) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "gnd", type: "pin_stub", start: { x: u(5), y: u(5.5) }, end: { x: u(5), y: u(7) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "txt", type: "text", position: { x: u(5), y: u(3.25) }, text: "LDO", anchor: "middle", fontSize: SCHEMATIC_TEXT.primitiveBody }
      ]
    },
    mcu: {
      symbolId: "mcu",
      name: "MCU",
      bounds: { x: 0, y: 0, width: u(12), height: u(10) },
      pins: [
        { pinId: "vcc", number: "24", name: "VCC", anchor: { x: u(6), y: 0 }, direction: "up" },
        { pinId: "gnd", number: "12", name: "GND", anchor: { x: u(6), y: u(10) }, direction: "down" },
        { pinId: "swdio", number: "34", name: "SWDIO", anchor: { x: u(12), y: u(3) }, direction: "right" },
        { pinId: "swclk", number: "37", name: "SWCLK", anchor: { x: u(12), y: u(5) }, direction: "right" },
        { pinId: "uart_tx", number: "18", name: "TX", anchor: { x: u(12), y: u(7.5) }, direction: "right" },
        { pinId: "uart_rx", number: "17", name: "RX", anchor: { x: 0, y: u(7.5) }, direction: "left" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: u(1.5), y: u(1.5) }, width: u(9), height: u(7), stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbolStrong },
        { id: "vcc", type: "pin_stub", start: { x: u(6), y: 0 }, end: { x: u(6), y: u(1.5) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "gnd", type: "pin_stub", start: { x: u(6), y: u(8.5) }, end: { x: u(6), y: u(10) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "swdio", type: "pin_stub", start: { x: u(10.5), y: u(3) }, end: { x: u(12), y: u(3) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "swclk", type: "pin_stub", start: { x: u(10.5), y: u(5) }, end: { x: u(12), y: u(5) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "tx", type: "pin_stub", start: { x: u(10.5), y: u(7.5) }, end: { x: u(12), y: u(7.5) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "rx", type: "pin_stub", start: { x: 0, y: u(7.5) }, end: { x: u(1.5), y: u(7.5) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "txt", type: "text", position: { x: u(6), y: u(5.25) }, text: "MCU", anchor: "middle", fontSize: SCHEMATIC_TEXT.primitiveTitle }
      ]
    },
    debugger: {
      symbolId: "debugger",
      name: "Debug Header",
      bounds: { x: 0, y: 0, width: u(8), height: u(8) },
      pins: [
        { pinId: "swdio", number: "2", name: "SWDIO", anchor: { x: 0, y: u(2) }, direction: "left" },
        { pinId: "swclk", number: "4", name: "SWCLK", anchor: { x: 0, y: u(4) }, direction: "left" },
        { pinId: "gnd", number: "3", name: "GND", anchor: { x: 0, y: u(6) }, direction: "left" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: u(1.5), y: u(1) }, width: u(5), height: u(6), stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "swdio", type: "pin_stub", start: { x: 0, y: u(2) }, end: { x: u(1.5), y: u(2) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "swclk", type: "pin_stub", start: { x: 0, y: u(4) }, end: { x: u(1.5), y: u(4) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "gnd", type: "pin_stub", start: { x: 0, y: u(6) }, end: { x: u(1.5), y: u(6) }, stroke: "#111827", strokeWidth: SCHEMATIC_STROKE.symbol },
        { id: "txt", type: "text", position: { x: u(4), y: u(4.125) }, text: "SWD", anchor: "middle", fontSize: SCHEMATIC_TEXT.primitiveSmall }
      ]
    }
  },
  pages: [
    {
      pageId: "page-power",
      title: "Power Input",
      size: { width: u(176), height: u(112) },
      instances: [
        {
          instanceId: "j1",
          symbolId: "usb-c-input",
          refdes: "J1",
          value: "USB-C",
          position: { x: u(8), y: u(10) },
          rotation: 0,
          mirror: false
        },
        {
          instanceId: "u2",
          symbolId: "ldo",
          refdes: "U2",
          value: "3V3 LDO",
          position: { x: u(28), y: u(8) },
          rotation: 0,
          mirror: false
        }
      ],
      wires: [
        {
          wireId: "wire-vbus",
          netId: "net-vbus",
          style: "power",
          points: [
            { x: u(16), y: u(11.5) },
            { x: u(20), y: u(11.5) },
            { x: u(20), y: u(10) },
            { x: u(28), y: u(10) }
          ]
        },
        {
          wireId: "wire-gnd-1",
          netId: "net-gnd",
          style: "ground",
          points: [
            { x: u(16), y: u(14.5) },
            { x: u(20), y: u(14.5) },
            { x: u(20), y: u(18) },
            { x: u(33), y: u(18) },
            { x: u(33), y: u(15) }
          ]
        },
        {
          wireId: "wire-3v3",
          netId: "net-3v3",
          style: "power",
          points: [
            { x: u(38), y: u(10) },
            { x: u(48), y: u(10) },
            { x: u(48), y: u(7.5) }
          ]
        }
      ],
      labels: [
        { labelId: "lbl-vbus", netId: "net-vbus", text: "VBUS", position: { x: u(21), y: u(10.75) }, orientation: 0 },
        { labelId: "lbl-3v3", netId: "net-3v3", text: "+3V3", position: { x: u(48.75), y: u(8.125) }, orientation: 0 },
        { labelId: "lbl-gnd", netId: "net-gnd", text: "GND", position: { x: u(33.5), y: u(18.875) }, orientation: 0 }
      ],
      junctions: [
        { junctionId: "junc-gnd", position: { x: u(20), y: u(14.5) } },
        { junctionId: "junc-vbus", position: { x: u(20), y: u(11.5) } }
      ],
      markers: []
    },
    {
      pageId: "page-core",
      title: "MCU Core",
      size: { width: u(200), height: u(128) },
      instances: [
        {
          instanceId: "u1",
          symbolId: "mcu",
          refdes: "U1",
          value: "STM32",
          position: { x: u(34), y: u(16) },
          rotation: 0,
          mirror: false
        },
        {
          instanceId: "j2",
          symbolId: "debugger",
          refdes: "J2",
          value: "SWD",
          position: { x: u(62), y: u(20) },
          rotation: 0,
          mirror: false
        },
        {
          instanceId: "x1",
          symbolId: "missing-symbol",
          refdes: "X1",
          value: "Future Sensor",
          position: { x: u(12), y: u(34) },
          rotation: 90,
          mirror: false
        }
      ],
      wires: [
        {
          wireId: "wire-3v3-u1",
          netId: "net-3v3",
          style: "power",
          points: [
            { x: u(40), y: u(16) },
            { x: u(40), y: u(11) },
            { x: u(48), y: u(11) }
          ]
        },
        {
          wireId: "wire-gnd-u1",
          netId: "net-gnd",
          style: "ground",
          points: [
            { x: u(40), y: u(26) },
            { x: u(40), y: u(31) },
            { x: u(48), y: u(31) }
          ]
        },
        {
          wireId: "wire-swdio",
          netId: "net-swdio",
          style: "signal",
          points: [
            { x: u(46), y: u(19) },
            { x: u(54), y: u(19) },
            { x: u(54), y: u(22) },
            { x: u(62), y: u(22) }
          ]
        },
        {
          wireId: "wire-swclk",
          netId: "net-swclk",
          style: "clock",
          points: [
            { x: u(46), y: u(21) },
            { x: u(54), y: u(21) },
            { x: u(54), y: u(24) },
            { x: u(62), y: u(24) }
          ]
        }
      ],
      labels: [
        { labelId: "lbl-3v3-core", netId: "net-3v3", text: "+3V3", position: { x: u(48.75), y: u(11.625) }, orientation: 0 },
        { labelId: "lbl-gnd-core", netId: "net-gnd", text: "GND", position: { x: u(48.75), y: u(31.625) }, orientation: 0 },
        { labelId: "lbl-swdio", netId: "net-swdio", text: "SWDIO", position: { x: u(54.75), y: u(18.375) }, orientation: 0 },
        { labelId: "lbl-swclk", netId: "net-swclk", text: "SWCLK", position: { x: u(54.75), y: u(22.75) }, orientation: 0 }
      ],
      junctions: [
        { junctionId: "junc-swdio", position: { x: u(54), y: u(19) } },
        { junctionId: "junc-swclk", position: { x: u(54), y: u(21) } }
      ],
      markers: [
        {
          markerId: "m1",
          kind: "warning",
          position: { x: u(14), y: u(34) },
          message: "Reserved area for future sensor block."
        }
      ]
    }
  ],
  nets: [
    { netId: "net-vbus", name: "VBUS", style: "power" },
    { netId: "net-3v3", name: "+3V3", style: "power" },
    { netId: "net-gnd", name: "GND", style: "ground" },
    { netId: "net-swdio", name: "SWDIO", style: "signal" },
    { netId: "net-swclk", name: "SWCLK", style: "clock" }
  ],
  metadata: {
    title: "OpenPCB Schematic Preview Demo",
    source: "mock-ts-geometry"
  }
};
