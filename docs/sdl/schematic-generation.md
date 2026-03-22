# SDL to Schematic Generation Guide

## Purpose
This document describes how SDL semantic objects should be interpreted for schematic generation planning.
It does not define a concrete generator implementation.

## Input Contract
- Input is a semantically valid SDL module.
- Component, pin, port, and net references are resolved.
- Constraint objects are available as generation hints.

## Mapping Model
- `component` maps to schematic symbols with instance references.
- `net` maps to logical connectivity edges.
- `port` maps to sheet or module interface markers.
- `constraint` maps to annotation or rule metadata.

## Determinism Requirements
- Same SDL input should produce stable symbol/net graph topology.
- Non-semantic ordering differences should not change generated graph meaning.

## Open Integration Points
- Symbol library resolution policy.
- Multi-sheet partitioning strategy.
- Annotation style policy for warnings and unresolved hints.
