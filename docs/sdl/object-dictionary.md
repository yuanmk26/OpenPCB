# SDL Object Dictionary

## Purpose
This dictionary defines SDL semantic entities and statements for the engineering DSL surface.
It is not a low-level IR field table.

## Language-Shape Positioning
- SDL entities are expressed as design statements (`module`, `interface`, `inst`, `connect`, `topology`, `require`).
- Example style should prioritize design readability and review, not config serialization style.
- Library internals (symbol/pad/pin metadata) may exist, but they are not the primary authoring surface.

## Module
Represents a first-class design unit.

Core semantics:
- Has a unique module name.
- May be parameterized (`module Name(param=value)`).
- Defines ports, instances, and intent statements.

## Interface
Represents reusable port bundles and protocol contracts.

Core semantics:
- Defines typed members (`tx: Output`, `gnd: Ground`).
- Enables interface-first module boundaries.
- Can be used by ports and exposed instance interfaces.

## Port
Represents module external connection points.

Core semantics:
- Declared as `port name: Type` where type can be scalar direction/electrical type or named interface.
- May participate in `connect`, `tie`, `map`, and `topology`.

## Instance (`inst`)
Represents an instantiated module or library part.

Core semantics:
- Declared as `inst id: Type(args...)`.
- Can carry role tags (`[role=...]`) for review and agent operations.
- Exposes endpoints and sub-interfaces used in connectivity statements.

## Net
Represents an explicit named electrical grouping in concise statement form.

Core semantics:
- Declared as `net name: [endpoint_a, endpoint_b, ...]`.
- Used when explicit net identity is required for rules, diagnostics, and review.

## Connect
Represents direct connectivity action.

Core semantics:
- Forward fanout form: `connect a -> [b, c]`.
- Bidirectional form: `connect a <-> b`.
- Should be preferred for immediate readability of "what connects to what".

## Expose
Represents interface export from instance scope to module scope.

Core semantics:
- Declared as `expose inst.path as module_port_or_interface`.

## Tie
Represents electrical equivalence between named signals or nets.

Core semantics:
- Declared as `tie lhs = rhs`.

## Topology
Represents ordered connectivity path intent.

Core semantics:
- Declared as `topology name: a => b => c`.
- Used when ordering matters and is not captured by raw connectivity alone.

## Constrain and Require
Two distinct intent categories:
- `constrain`: hard machine-checkable rule.
- `require`: engineering requirement intent, normative but potentially profile-dependent for enforcement.

## Place and Domain
- `place`: human-readable placement intent for components or groups.
- `domain`: named functional/electrical context used for partitioning and rule targeting.

## Map
Represents interface/port mapping across module boundaries.

Core semantics:
- Declared as `map source -> target`.
- Commonly used in top-level composition modules.

## Stability Notes
- This dictionary defines semantic intent for v0.1 draft and may refine wording in later versions.
- Any future parser/IR representation must preserve these statement-level meanings.
