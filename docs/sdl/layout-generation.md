# SDL to Layout Generation Guide

## Purpose
This document outlines how SDL intent can inform downstream PCB layout preparation.
It is a planning contract, not an autorouter specification.

## Input Expectations
- Schematic-level connectivity is complete and validated.
- Components include enough metadata for package/placement intent.
- Net classes or constraints exist where routing intent matters.

## Handoff Artifacts
- Component instance list with package hints.
- Netlist-level connectivity.
- Constraint and class annotations relevant to placement/routing.

## Expected Behaviors
- Preserve connectivity identity from SDL through handoff.
- Preserve explicit constraint intent where representable.
- Report unsupported or lossy mappings as diagnostics.

## Deferred Topics
- Geometry-specific constraint syntax.
- Differential pair and length tuning formalization.
- Layer stack and manufacturing rule binding.
