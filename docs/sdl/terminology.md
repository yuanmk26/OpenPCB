# SDL Terminology

## Purpose
This document defines stable terms used by SDL specs, guides, and examples.
If a term conflicts with casual usage, this document takes precedence.

## Core Terms
- **SDL**: Schematic Description Language used by OpenPCB.
- **Module**: Named design unit that contains components, nets, ports, and parameters.
- **Component**: Electrical part instance with a symbol footprint reference and pins.
- **Pin**: Connection point on a component.
- **Port**: External interface endpoint of a module.
- **Net**: Electrical connectivity group linking pins and ports.
- **Constraint**: Design rule or intent condition attached to objects.
- **Variant**: Conditional configuration branch for BOM or connectivity differences.
- **Patch**: Minimal, deterministic edit operation applied to SDL content.

## Identity Terms
- **Object ID**: Stable identifier for object-level references in patches and diagnostics.
- **Path**: Hierarchical reference string to locate nested objects.
- **Reference Name**: Human-facing short name such as `U1`, `R3`, `Net_3V3`.

## Semantic Terms
- **Normalization**: Canonical representation step that removes superficial differences.
- **Resolution**: Process of mapping names and references to concrete objects.
- **Validation Error**: Rule violation that blocks acceptance.
- **Validation Warning**: Rule concern that does not block acceptance.

## Document Usage Rules
- New terms should be added here before broad usage.
- Existing term meanings should not be silently changed.
