# SDL Syntax Specification (Draft v0.1)

## Purpose
This document defines the recommended SDL surface syntax for OpenPCB.
The style is indentation-first engineering DSL focused on design expression and review.

## Syntax Positioning
- SDL syntax serves engineering intent clarity first.
- It is not designed as a low-level config serialization format.
- Formal parser grammar can be tightened later; current goal is clear and consistent authoring semantics.

## Canonical Style
- Use indentation to express structure.
- Use statement-oriented forms.
- Keep interface/module/connectivity/intent statements explicit.

Non-canonical style in v0.1:
- `module "name" { ... }`
- key-value heavy configuration style
- hiding constraints/requirements inside generic metadata blobs

## Lexical Basics
- Encoding: UTF-8.
- Comment prefix: `#`.
- Indentation: 4 spaces.
- Identifier: `[A-Za-z_][A-Za-z0-9_]*`.
- Values may include engineering units (`3.3V`, `10uF`, `100MHz`).

## Required Statement Set
### `module`
Defines reusable design unit. Parentheses declare parameters.

```text
module LDO_Block(vout=3.3V):
    ...
```

### `interface`
Defines structured heterogeneous boundary contract.

```text
interface I2C:
    scl: InOut
    sda: InOut
```

### `inst`
Instantiates component type or module with arguments.

```text
inst u_ldo: AMS1117(vout=vout) [role=regulator]
inst mcu0: STM32_Min_System(hse=8MHz)
```

### `port`
Declares module boundary endpoint.

```text
port vdd: PowerIn
port swd: SWD
```

### `net`
Declares named connectivity equivalence class.

```text
net vdd_3v3: [u_ldo.vout, mcu0.vdd, sensor0.vdd]
```

### `group`
Declares logical non-electrical grouping.

```text
group bringup_core: [pwr0, mcu0, dbg0]
```

### `connect`
Declares direct connectivity intent.

```text
connect vin -> [u_ldo.vin, c_in.1]
connect usb <-> j_usb.usb2
connect i2c.scl -> [u_sensor.scl, r_scl.2]
```

### `expose`
Exports internal instance endpoint/interface to module boundary.

```text
expose j_swd.swd as swd
```

### `tie`
Declares fixed equivalence binding.

```text
tie agnd = gnd
```

### `topology`
Declares ordered signal path semantics.

```text
topology usb_dp: j_usb.dp => d_esd.dp => usb.dp
```

### `constrain`
Declares machine-checkable rule or preference.

```text
constrain net vout_main ripple < 50mV
constrain bus i2c frequency <= 400kHz
```

### `require`
Declares engineering obligation.

```text
require decoupling for u_mcu
require protection for j_usb
```

### `place`
Declares placement hint (not final coordinates).

```text
place [u_ldo, c_in, c_out] compact
place j_usb on board_edge
```

### `domain`
Declares semantic domain object.

```text
domain pwr_3v3:
    class: Power
    source: usb0.vbus_out
    return: gnd_global
    provider: pwr0
    consumers: [mcu0, sns0, dbg0]
```

### `map`
Declares explicit interface/member mapping.

```text
map mcu0.i2c0 -> sns0.i2c
map debug_port.nrst -> mcu0.swd.nreset
```

### `bus` / `vector`
Declares homogeneous indexed signals.

```text
bus gpio[0..15]: DigitalIO
vector adc_in[0..3]: AnalogIn
```

## Parameter and Instantiation Rules
- `module Name(...)`: parameter declaration at module definition.
- `inst x: Name(...)`: argument assignment at instance site.
- Omitted argument values use module-defined defaults.

## Interface and Mapping Rules (Syntax-Level)
- Interface members are addressed using dotted paths.
- Interface-to-interface connect may be direct if members align.
- Use `map` when member names are not identical.

## Minimal Composite Example
```text
interface SWD:
    swdio: InOut
    swclk: Input
    nreset: InOut
    vtref: PowerIn

module Debug_Block:
    port swd: SWD
    port gnd: Ground

    inst j_swd: SWD_Header_2x5 [role=debug_connector]
    expose j_swd.swd as swd
    connect j_swd.gnd -> gnd
    require accessible for j_swd
    place j_swd near board_edge
```

## Draft Notes
- This document describes syntax shape and required capabilities, not full parser EBNF.
- Semantics are defined in `semantic-rules.md`.
