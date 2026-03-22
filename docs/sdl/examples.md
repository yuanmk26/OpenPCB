# SDL Examples Catalog

## Purpose
This file maps each draft example to its design intent.
Examples are minimal and are not full production schematics.

## Example List
- `examples/stm32-min-system.opsdl`: MCU minimum system with clocks, reset, and power.
- `examples/ldo-block.opsdl`: Linear regulator power conditioning block.
- `examples/usb-input-block.opsdl`: USB power/data input front-end block.
- `examples/debug-block.opsdl`: Debug/programming connector block.
- `examples/sensor-i2c-block.opsdl`: I2C sensor submodule with pull-ups.
- `examples/top-board-with-submodules.opsdl`: Top-level board composition using submodules.

## How to Read
1. Start from `module`.
2. Inspect `component`, `port`, and `net` blocks.
3. Compare naming and structure with `syntax-spec.md` and `semantic-rules.md`.

## Known Simplifications
- Footprints and exact pin maps are intentionally abbreviated.
- Constraints are shown as examples, not complete manufacturing rules.
