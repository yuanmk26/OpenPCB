# SDL to Layout Generation Guide

## Purpose
This document defines the layered chain from SDL semantics to PCB layout output.
The goal is semantic separation before geometry commitment.

## Canonical Chain
`SDL -> footprint semantic model -> PCB logical layout model -> PCB geometry model -> layout file / PCB render`

## Key Rules
- Footprint semantics are not only "choose one footprint name".
- SDL should not be bound directly to final geometry in current phase.
- Keep footprint semantics and layout logic as explicit intermediate layers.

## Layer Responsibilities
### 1. SDL
- Provides module/interface/connectivity/domain/constraint/placement semantics.

### 2. Footprint Semantic Model
Minimum responsibilities:
- instance-to-footprint mapping
- pin-pad mapping
- footprint physical role
- orientation preference
- placement preference hints

### 3. PCB Logical Layout Model
Minimum responsibilities:
- placement groups
- layout constraints
- routing semantics
- diff pair / clock / power class intent
- board edge anchors
- power regions / logical placement regions

### 4. PCB Geometry Model
Geometry-only responsibilities:
- x/y coordinates
- rotation
- tracks
- vias
- copper zones
- board outline
- keepout regions

### 5. Layout File / PCB Render
- Final output for PCB tools and visual rendering.
- Should preserve logical intent decisions from upstream layers.

## OpenPCB v0.1 Guidance
- Prioritize clean semantic layering over early geometry detail expansion.
- Keep domain, topology, and requirement intent available to logical layout stage.
