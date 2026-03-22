# SDL Examples Catalog

## Purpose
This file maps each draft `.opsdl` example to concrete design intent.
Examples use the canonical indentation engineering DSL style.

## Example List
- `examples/stm32-min-system.opsdl`: parameterized MCU base module with debug and I2C interfaces.
- `examples/ldo-block.opsdl`: parameterized regulator module with direct power connectivity and placement intent.
- `examples/usb-input-block.opsdl`: USB input front-end with topology path intent and protection requirements.
- `examples/debug-block.opsdl`: debug connector module using interface-first exposure.
- `examples/sensor-i2c-block.opsdl`: sensor module with typed I2C interface, pull-ups, and simple constraints.
- `examples/top-board-with-submodules.opsdl`: top-level nested composition with `inst`, `map`, and cross-module connections.

## Style Expectations
- Examples are design-expression DSL, not low-level IR/config.
- Connectivity should be readable at first glance (`connect`, `tie`, `topology`).
- Interfaces and module boundaries should be explicit.
- `require` and `place` statements are separate from connectivity and should not be hidden in metadata.

## How to Read
1. Start from `interface` declarations and module signatures.
2. Inspect `inst`, `port`, and `map` to understand composition boundaries.
3. Read `connect`, `tie`, and `topology` as electrical intent.
4. Read `constrain`, `require`, and `place` as design intent and review targets.

## Known Simplifications
- Library part models and pad-level details are intentionally abbreviated.
- Rules are representative and not a complete manufacturing constraint deck.
