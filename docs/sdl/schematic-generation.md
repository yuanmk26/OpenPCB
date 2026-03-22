# SDL to Schematic Generation Guide

## Purpose
This document defines the layered transformation chain from SDL to schematic outputs.
It clarifies model boundaries and avoids direct text-to-file shortcuts.

## Canonical Chain
`SDL -> parser/loader -> normalized SDL/runtime structure -> schematic logical model -> schematic geometry model -> schematic file / GUI render`

## Key Rules
- SDL is not equal to final schematic file format.
- Generation should not be implemented as direct string conversion.
- A schematic logical model is required as an explicit middle layer.
- Symbol semantics are only one part of the logical model.

## Layer Responsibilities
### 1. SDL
- Authoritative source for module, interface, connectivity, constraints, and hints.

### 2. Parser / Loader
- Parses syntax and resolves references.
- Produces normalized runtime structure for deterministic downstream behavior.

### 3. Normalized SDL / Runtime Structured Representation
- Stable semantic graph for instances, ports, interfaces, nets, domains, topology, requirements.
- Primary execution target for validation and generation tools.

### 4. Schematic Logical Model
Minimum responsibilities:
- Symbol instance set.
- Sheet/page hierarchy organization.
- Rendered net and label strategy.
- `expose` to hierarchical port conversion.
- Wire-vs-net-label-vs-power-symbol expression strategy.

### 5. Schematic Geometry Model
Geometry-only responsibilities:
- Symbol coordinates.
- Symbol orientation/rotation.
- Wire segments.
- Label positions.
- Junction positions.

### 6. Schematic File / GUI Render
- File export and GUI rendering from geometry model.
- No semantic reinterpretation that contradicts SDL contract.

## OpenPCB v0.1 Guidance
- Keep logical and geometry layers explicit in design docs and implementation.
- Do not collapse logical model into "symbol list only".
