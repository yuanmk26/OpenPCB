# SDL Object Dictionary (Authoritative v0.1 Draft)

## Purpose
This document defines the canonical SDL object system for OpenPCB v0.1.
It is organized into four layers and is the most detailed SDL reference in this doc set.

## Modeling Notes
- SDL is an engineering DSL, not a low-level IR serialization format.
- Objects here describe semantic intent; runtime structures derive from SDL statements.
- `Component` is treated as a library/type entity referenced by `inst`; v0.1 does not require top-level `component` declarations.

## Layer A: Structural Layer
### Module
Definition:
- Highest-level structural design unit.
- Supports parameter declaration (`module Name(param=...)`).
- Supports nested module composition through module instances.

Key semantics:
- Boundary is defined by ports and exposed interfaces.
- Parent modules should connect through boundary objects, not child-local private nets.

Typical statements:
- `module`
- `port`
- `inst` (module target)
- `group`

### Component
Definition:
- Library/type-level part definition (for example MCU family, regulator part, ESD part).

Key semantics:
- Identifies available pins/electrical behavior contract for instances.
- Is referenced by `inst` when target is a part type.

### Instance (`inst`)
Definition:
- Concrete instantiated object with stable local identity.

Key semantics:
- May target a component type or another module.
- Can include role tags and instance arguments.
- Is the primary anchor for RefPath references in patch and validation operations.

### Pin
Definition:
- Electrical endpoint on an instance.

Key semantics:
- Participates in connect/topology semantics.
- Carries electrical type metadata in resolved semantics.

### Port
Definition:
- Boundary endpoint on a module.

Key semantics:
- Can be scalar type or interface type.
- Is the primary legal connection point for parent-child integration.

### Interface
Definition:
- Structured heterogeneous set of interface members (for example SWD, I2C, USB2).

Key semantics:
- First-class unit for module contracts and connect/map operations.
- Enables interface-first reasoning for both humans and agents.

### Interface Member
Definition:
- Named typed item inside an interface (for example `scl`, `sda`, `tx`, `rx`).

Key semantics:
- Can be auto-matched by name in interface-interface connections when compatible.
- Can be explicitly matched through `map` when names differ.

### Group
Definition:
- Logical collection of objects for organization, policy targeting, or placement intent.

Key semantics:
- Not equivalent to electrical connectivity.
- May drive constraints, requirements, or placement hints.

## Layer B: Connectivity Layer
### Net
Definition:
- Logical connectivity equivalence class.

Key semantics:
- Names and groups connected endpoints.
- Supports diagnostics, reporting, and downstream mapping.

### Connect
Definition:
- Explicit connectivity statement.

Key semantics:
- Supports pin-net, pin-pin, interface-interface, and fanout connection patterns.
- Should be readable as direct engineering wiring intent.

### Expose
Definition:
- Boundary-export statement that maps internal instance endpoint/interface to module boundary.

Key semantics:
- Enables controlled hierarchical visibility.
- Supports clean parent-child composition.

### Tie
Definition:
- Explicit equivalence binding between endpoints/nets.

Key semantics:
- Used for fixed bindings and deliberate semantic aliasing.

### Topology
Definition:
- Ordered path semantics overlay for specific signal chains.

Key semantics:
- Not a replacement for net.
- Captures order-sensitive intent (for example connector -> protection -> transceiver path).

### Mapping (`map`)
Definition:
- Explicit correspondence mapping between endpoints/interface members.

Key semantics:
- Required when interface members do not match by name.
- Used in composition boundaries and interface adaptation.

### Bus / Vector
Definition:
- Homogeneous indexed signal collection.

Key semantics:
- Distinct from interface:
  - bus/vector: homogeneous indexed array.
  - interface: heterogeneous structured contract.

## Layer C: Engineering Semantics Layer
### Electrical Type
Definition:
- Electrical role classification of pin/port/interface member.

Examples:
- `PowerIn`, `PowerOut`, `Ground`, `Input`, `Output`, `InOut`, `Passive`.

### Role
Definition:
- Engineering purpose label for instances/modules/components.

Examples:
- `mcu`, `regulator`, `protection`, `external_connector`, `sensor`.

### Power Domain
Definition:
- Semantic power object describing power intent, not only a net label.

Minimum semantics:
- `source`
- `return`
- `provider`
- `consumers`

### Signal Class
Definition:
- Signal behavior category used by constraint and routing semantics.

Examples:
- `power`, `ground`, `reset`, `clock`, `diffpair`, `analog_sensitive`.

### Connector Category
Definition:
- External connector class used for policy and validation.

Examples:
- `usb_connector`, `debug_connector`, `sensor_connector`.

## Layer D: Constraints and Validation Layer
### Constraint (`constrain`)
Definition:
- Machine-checkable rule or preference.

Semantics:
- Targets object/path/group/domain/topology context.
- Should produce deterministic pass/fail or graded diagnostics.

### Requirement (`require`)
Definition:
- Engineering obligation that must be satisfied by design realization.

Semantics:
- Examples: decoupling, protection, pullup, return-path requirement.
- Can map to one or more concrete checks.

### Placement Hint (`place`)
Definition:
- Design-time placement guidance.

Semantics:
- Intent-level only, not final geometry coordinates.
- Used by downstream schematic/layout generation stages.

### Completeness Check
Definition:
- Validation family that guards minimum design completeness before export/generation.

Minimum scope:
- reference legality
- duplicate naming
- interface completeness
- requirement satisfaction
- power domain rationality
- topology legality
- external connector protection requirements

### RefPath
Definition:
- Stable reference path to internal semantic target.

Example:
- `u_mcu.power.vdd[0]`

Semantics:
- Canonical target form for patch operations and diagnostics.

## Stability and Evolution
- v0.1 prioritizes clarity of semantic contracts over exhaustive formal grammar.
- Future parser/runtime models must preserve these object meanings and layer boundaries.
