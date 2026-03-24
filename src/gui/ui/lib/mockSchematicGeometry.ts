import type { SchematicGeometry } from "@/types/schematic";

export const mockSchematicGeometry: SchematicGeometry = {
  version: "1.0.0",
  symbolLibrary: {
    "usb-c-input": {
      symbolId: "usb-c-input",
      name: "USB-C Input",
      bounds: { x: 0, y: 0, width: 110, height: 90 },
      pins: [
        { pinId: "vbus", number: "A4", name: "VBUS", anchor: { x: 110, y: 20 }, direction: "right" },
        { pinId: "gnd", number: "A1", name: "GND", anchor: { x: 110, y: 70 }, direction: "right" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: 10, y: 10 }, width: 80, height: 70, stroke: "#dfe8f1" },
        { id: "p1", type: "pin_stub", start: { x: 90, y: 20 }, end: { x: 110, y: 20 }, stroke: "#dfe8f1" },
        { id: "p2", type: "pin_stub", start: { x: 90, y: 70 }, end: { x: 110, y: 70 }, stroke: "#dfe8f1" },
        { id: "t1", type: "text", position: { x: 50, y: 48 }, text: "USB-C", anchor: "middle", fontSize: 16 }
      ]
    },
    ldo: {
      symbolId: "ldo",
      name: "LDO Regulator",
      bounds: { x: 0, y: 0, width: 140, height: 110 },
      pins: [
        { pinId: "vin", number: "1", name: "VIN", anchor: { x: 0, y: 28 }, direction: "left" },
        { pinId: "gnd", number: "2", name: "GND", anchor: { x: 70, y: 110 }, direction: "down" },
        { pinId: "vout", number: "3", name: "VOUT", anchor: { x: 140, y: 28 }, direction: "right" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: 25, y: 12 }, width: 90, height: 70, stroke: "#dfe8f1" },
        { id: "vin", type: "pin_stub", start: { x: 0, y: 28 }, end: { x: 25, y: 28 }, stroke: "#dfe8f1" },
        { id: "vout", type: "pin_stub", start: { x: 115, y: 28 }, end: { x: 140, y: 28 }, stroke: "#dfe8f1" },
        { id: "gnd", type: "pin_stub", start: { x: 70, y: 82 }, end: { x: 70, y: 110 }, stroke: "#dfe8f1" },
        { id: "txt", type: "text", position: { x: 70, y: 48 }, text: "LDO", anchor: "middle", fontSize: 16 }
      ]
    },
    mcu: {
      symbolId: "mcu",
      name: "MCU",
      bounds: { x: 0, y: 0, width: 180, height: 160 },
      pins: [
        { pinId: "vcc", number: "24", name: "VCC", anchor: { x: 90, y: 0 }, direction: "up" },
        { pinId: "gnd", number: "12", name: "GND", anchor: { x: 90, y: 160 }, direction: "down" },
        { pinId: "swdio", number: "34", name: "SWDIO", anchor: { x: 180, y: 50 }, direction: "right" },
        { pinId: "swclk", number: "37", name: "SWCLK", anchor: { x: 180, y: 80 }, direction: "right" },
        { pinId: "uart_tx", number: "18", name: "TX", anchor: { x: 180, y: 120 }, direction: "right" },
        { pinId: "uart_rx", number: "17", name: "RX", anchor: { x: 0, y: 120 }, direction: "left" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: 20, y: 20 }, width: 140, height: 120, stroke: "#dfe8f1" },
        { id: "vcc", type: "pin_stub", start: { x: 90, y: 0 }, end: { x: 90, y: 20 }, stroke: "#dfe8f1" },
        { id: "gnd", type: "pin_stub", start: { x: 90, y: 140 }, end: { x: 90, y: 160 }, stroke: "#dfe8f1" },
        { id: "swdio", type: "pin_stub", start: { x: 160, y: 50 }, end: { x: 180, y: 50 }, stroke: "#dfe8f1" },
        { id: "swclk", type: "pin_stub", start: { x: 160, y: 80 }, end: { x: 180, y: 80 }, stroke: "#dfe8f1" },
        { id: "tx", type: "pin_stub", start: { x: 160, y: 120 }, end: { x: 180, y: 120 }, stroke: "#dfe8f1" },
        { id: "rx", type: "pin_stub", start: { x: 0, y: 120 }, end: { x: 20, y: 120 }, stroke: "#dfe8f1" },
        { id: "txt", type: "text", position: { x: 90, y: 82 }, text: "MCU", anchor: "middle", fontSize: 18 }
      ]
    },
    debugger: {
      symbolId: "debugger",
      name: "Debug Header",
      bounds: { x: 0, y: 0, width: 110, height: 120 },
      pins: [
        { pinId: "swdio", number: "2", name: "SWDIO", anchor: { x: 0, y: 30 }, direction: "left" },
        { pinId: "swclk", number: "4", name: "SWCLK", anchor: { x: 0, y: 60 }, direction: "left" },
        { pinId: "gnd", number: "3", name: "GND", anchor: { x: 0, y: 90 }, direction: "left" }
      ],
      graphics: [
        { id: "body", type: "rect", origin: { x: 20, y: 15 }, width: 70, height: 90, stroke: "#dfe8f1" },
        { id: "swdio", type: "pin_stub", start: { x: 0, y: 30 }, end: { x: 20, y: 30 }, stroke: "#dfe8f1" },
        { id: "swclk", type: "pin_stub", start: { x: 0, y: 60 }, end: { x: 20, y: 60 }, stroke: "#dfe8f1" },
        { id: "gnd", type: "pin_stub", start: { x: 0, y: 90 }, end: { x: 20, y: 90 }, stroke: "#dfe8f1" },
        { id: "txt", type: "text", position: { x: 55, y: 62 }, text: "SWD", anchor: "middle", fontSize: 14 }
      ]
    }
  },
  pages: [
    {
      pageId: "page-power",
      title: "Power Input",
      size: { width: 1400, height: 900 },
      instances: [
        {
          instanceId: "j1",
          symbolId: "usb-c-input",
          refdes: "J1",
          value: "USB-C",
          position: { x: 120, y: 150 },
          rotation: 0,
          mirror: false,
          refdesPosition: { x: 130, y: 124 },
          valuePosition: { x: 130, y: 262 }
        },
        {
          instanceId: "u2",
          symbolId: "ldo",
          refdes: "U2",
          value: "3V3 LDO",
          position: { x: 460, y: 120 },
          rotation: 0,
          mirror: false,
          refdesPosition: { x: 488, y: 92 },
          valuePosition: { x: 478, y: 248 }
        }
      ],
      wires: [
        {
          wireId: "wire-vbus",
          netId: "net-vbus",
          style: "power",
          points: [
            { x: 230, y: 170 },
            { x: 320, y: 170 },
            { x: 320, y: 148 },
            { x: 460, y: 148 }
          ]
        },
        {
          wireId: "wire-gnd-1",
          netId: "net-gnd",
          style: "ground",
          points: [
            { x: 230, y: 220 },
            { x: 320, y: 220 },
            { x: 320, y: 300 },
            { x: 530, y: 300 },
            { x: 530, y: 230 }
          ]
        },
        {
          wireId: "wire-3v3",
          netId: "net-3v3",
          style: "power",
          points: [
            { x: 600, y: 148 },
            { x: 770, y: 148 },
            { x: 770, y: 110 }
          ]
        }
      ],
      labels: [
        { labelId: "lbl-vbus", netId: "net-vbus", text: "VBUS", position: { x: 332, y: 158 }, orientation: 0 },
        { labelId: "lbl-3v3", netId: "net-3v3", text: "+3V3", position: { x: 782, y: 118 }, orientation: 0 },
        { labelId: "lbl-gnd", netId: "net-gnd", text: "GND", position: { x: 540, y: 314 }, orientation: 0 }
      ],
      junctions: [
        { junctionId: "junc-gnd", position: { x: 320, y: 220 } },
        { junctionId: "junc-vbus", position: { x: 320, y: 170 } }
      ],
      markers: []
    },
    {
      pageId: "page-core",
      title: "MCU Core",
      size: { width: 1600, height: 1000 },
      instances: [
        {
          instanceId: "u1",
          symbolId: "mcu",
          refdes: "U1",
          value: "STM32",
          position: { x: 540, y: 220 },
          rotation: 0,
          mirror: false,
          refdesPosition: { x: 596, y: 190 },
          valuePosition: { x: 586, y: 414 }
        },
        {
          instanceId: "j2",
          symbolId: "debugger",
          refdes: "J2",
          value: "SWD",
          position: { x: 980, y: 280 },
          rotation: 0,
          mirror: false,
          refdesPosition: { x: 1004, y: 248 },
          valuePosition: { x: 1004, y: 420 }
        },
        {
          instanceId: "x1",
          symbolId: "missing-symbol",
          refdes: "X1",
          value: "Future Sensor",
          position: { x: 180, y: 520 },
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
            { x: 630, y: 220 },
            { x: 630, y: 150 },
            { x: 770, y: 150 }
          ]
        },
        {
          wireId: "wire-gnd-u1",
          netId: "net-gnd",
          style: "ground",
          points: [
            { x: 630, y: 380 },
            { x: 630, y: 450 },
            { x: 770, y: 450 }
          ]
        },
        {
          wireId: "wire-swdio",
          netId: "net-swdio",
          style: "signal",
          points: [
            { x: 720, y: 270 },
            { x: 850, y: 270 },
            { x: 850, y: 310 },
            { x: 980, y: 310 }
          ]
        },
        {
          wireId: "wire-swclk",
          netId: "net-swclk",
          style: "clock",
          points: [
            { x: 720, y: 300 },
            { x: 850, y: 300 },
            { x: 850, y: 340 },
            { x: 980, y: 340 }
          ]
        }
      ],
      labels: [
        { labelId: "lbl-3v3-core", netId: "net-3v3", text: "+3V3", position: { x: 782, y: 160 }, orientation: 0 },
        { labelId: "lbl-gnd-core", netId: "net-gnd", text: "GND", position: { x: 782, y: 460 }, orientation: 0 },
        { labelId: "lbl-swdio", netId: "net-swdio", text: "SWDIO", position: { x: 862, y: 260 }, orientation: 0 },
        { labelId: "lbl-swclk", netId: "net-swclk", text: "SWCLK", position: { x: 862, y: 330 }, orientation: 0 }
      ],
      junctions: [
        { junctionId: "junc-swdio", position: { x: 850, y: 270 } },
        { junctionId: "junc-swclk", position: { x: 850, y: 300 } }
      ],
      markers: [
        {
          markerId: "m1",
          kind: "warning",
          position: { x: 208, y: 520 },
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
