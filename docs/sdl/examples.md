# SDL Examples Catalog

## Purpose
This file maps each example to required SDL capabilities in the current OpenPCB phase.
Examples are architecture-aligned and should be read as semantic design expressions, not IR/config dumps.

## Capability Matrix
| Example | Required Capabilities |
| --- | --- |
| `stm32-min-system.opsdl` | MCU core, decoupling, reset/boot pins, basic power nets, interface mapping |
| `ldo-block.opsdl` | Parameterized module, power in/out, compact placement hint |
| `usb-input-block.opsdl` | External connector, protection, topology chain, board-edge placement |
| `debug-block.opsdl` | SWD interface, expose workflow |
| `sensor-i2c-block.opsdl` | I2C interface, pullup and decoupling requirement, sensor role |
| `top-board-with-submodules.opsdl` | Nested module composition, top-level wiring via ports/expose, domain/group organization |

## Reading Guide
1. Read module signatures and interfaces first.
2. Inspect instance graph and boundary ports.
3. Read connectivity (`connect`, `tie`, `topology`, `map`).
4. Read intent layer (`constrain`, `require`, `place`, `domain`, `group`).

## Review Checklist for Examples
- Uses module-first and interface-first structure.
- Does not rely on private child-net reach-through from parent module.
- Separates connectivity from constraints/requirements/placement hints.
- Includes stable references suitable for patch-style agent operations.
