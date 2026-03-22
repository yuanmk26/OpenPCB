# SDL Validation Guide

## Purpose
This guide defines the validation model for SDL v0.1.
Validation protects authoritative SDL quality before generation/export.

## Validation Layers
### 1. Syntax Layer
- Statement shape and indentation validity.
- Required statement tokens and argument forms.

### 2. Structural Layer
- Module/interface/instance/port definitions are coherent.
- Instantiation targets are legal (component type or module).
- Duplicate names in scope are rejected.

### 3. Connectivity Layer
- Endpoint RefPaths resolve.
- Connect/tie/net/topology/map references are legal.
- Interface connect consistency is validated.

### 4. Engineering Semantics Layer
- Electrical type compatibility checks.
- Role/domain/signal-class coherence checks.
- Connector category policy checks where applicable.

### 5. Constraints and Requirement Layer
- Constraint expression applicability and target validity.
- Requirement presence and satisfaction evidence.
- Placement-hint syntax and target validity.

## Required Completeness Checks (Minimum)
- Reference legality.
- Duplicate naming checks.
- Interface completeness.
- Requirement satisfaction.
- Power domain rationality.
- Topology legality.
- External connector protection checks.

## Diagnostic Contract
- Errors block acceptance.
- Warnings allow acceptance with explicit review requirement.
- Diagnostics should anchor to stable RefPath targets.

## Validation Profiles
- Core profile: mandatory language and semantic checks.
- Project profile: product-specific rule packs layered on top of core profile.
