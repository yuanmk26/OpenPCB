# SDL Validation Guide

## Purpose
This guide defines validation layers and expected outcomes for SDL documents.

## Validation Layers
- **Syntax validation**: token and block structure checks.
- **Semantic validation**: reference resolution and rule consistency.
- **Policy validation**: project-specific conventions and constraints.

## Minimum Checks
- One top-level module exists.
- Required fields for all known objects are present.
- All net endpoints resolve.
- No duplicate object ids in scope.

## Validation Output
- Deterministic diagnostics with severity, location, and message.
- Error blocks acceptance.
- Warning permits acceptance with traceable risk note.

## Profile Strategy
- Core profile: language-level mandatory checks.
- Project profile: additional domain constraints.
