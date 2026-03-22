# SDL Syntax Specification (Draft v0.1)

## Purpose
This document defines the recommended SDL surface syntax for `.opsdl` files.
The canonical style is an indentation-first engineering DSL for design expression, agent edits, and review.

## Canonical Surface Style
- SDL is written as statement-oriented design code, not JSON-like or block-config data.
- Indentation defines structure.
- Module and interface are first-class language entities.
- Connectivity is expressed with direct `connect`, `tie`, and `topology` statements.

The following styles are non-canonical in this phase:
- `module "name" { ... }`
- `key "value"`-heavy configuration shape
- net blocks used as generic config containers

## Lexical Conventions
- Encoding: UTF-8.
- Comments start with `#`.
- Indentation is significant and uses 4 spaces per level.
- Identifiers use `[A-Za-z_][A-Za-z0-9_]*`.
- Numeric values may include engineering units such as `3.3V`, `10uF`, `4.7k`.

## File Structure
A file may define one or more `interface` blocks and one or more `module` blocks.
A board-level file typically ends with one top-level composition module.

## Core Declarations
### `interface`
Defines reusable typed external contracts.

```text
interface UART:
    tx: Output
    rx: Input
```

### `module`
Defines a design unit. Parameterized modules are supported.

```text
module LDO_Block(vout=3.3V):
    port vin: PowerIn
    port gnd: Ground
    port vout: PowerOut
```

### `inst`
Creates a module or library part instance.

```text
inst u_ldo: AMS1117_3V3(vout=vout) [role=regulator]
inst mcu0: STM32_Min_System()
```

### `port`
Declares module ports with types or interfaces.

```text
port usb: USB2_Device
port swd: SWD
port gnd: Ground
```

### `net`
Declares explicit named nets in concise statement form.

```text
net vbus_raw: [j_usb.vbus, f_vbus.in]
net gnd: [j_usb.gnd, d_usb.gnd, gnd]
```

## Connectivity and Interface Binding
### `connect`
Direct connection expression for clear engineering readability.

```text
connect vin -> [u_ldo.vin, c_in.1]
connect usb <-> j_usb.usb2
```

### `expose`
Exports instance-internal signals/interfaces to module-level ports.

```text
expose j_swd.swd as swd
expose mcu0.uart_dbg as uart_dbg
```

### `tie`
Aliases two named nets or ports that must be electrically identical.

```text
tie agnd = gnd
tie shield_gnd = gnd
```

### `topology`
Defines ordered path intent when sequence matters.

```text
topology usb_dp: j_usb.dp => d_esd.dp => usb.dp
topology usb_dm: j_usb.dm => d_esd.dm => usb.dm
```

## Constraint and Intent Statements
### `constrain`
Hard, machine-checkable rule that should evaluate to pass/fail.

```text
constrain net vout ripple < 50mV
constrain pair usb_dp usb_dm skew < 20ps
```

### `require`
Engineering requirement intent. It is normative design intent and may map to checks over time.

```text
require decoupling for u_mcu
require protection for j_usb
```

### `place`
Placement intent at design-expression level.

```text
place [u_ldo, c_in, c_out] compact
place j_usb on board_edge
```

### `domain`
Declares or assigns functional/electrical domains.

```text
domain power_3v3: Power
domain usb_sig: HighSpeedDigital
```

### `map`
Maps interfaces or ports across module boundaries.

```text
map usb0.vbus_out -> pwr0.vin
map dbg0.swd -> mcu0.swd
```

## Integrated Example
```text
interface SWD:
    swdio: InOut
    swclk: Input
    nreset: InOut

module Debug_Block:
    port swd: SWD
    port gnd: Ground

    inst j_swd: SWD_Header_2x5 [role=debug_connector]
    expose j_swd.swd as swd
    connect j_swd.gnd -> gnd
    require accessible for j_swd
    place j_swd near board_edge
```

## Grammar and Evolution Notes
- This is a draft language contract and not yet a full formal grammar.
- Whitespace and comments are non-semantic except indentation level.
- Unknown statements are invalid unless explicitly enabled by a future extension profile.
