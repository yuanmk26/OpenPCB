# SDL Semantic Rules (Normative v0.1 Draft)

## Purpose
This document defines required meaning-level rules for SDL.
Syntactic validity alone is insufficient; designs must satisfy these semantic rules.

## Rule Severity
- `error`: blocks acceptance and downstream generation/export.
- `warning`: accepted with diagnostics and explicit review risk.

## 1. Module Hierarchy and Encapsulation
### Rule 1.1: Module Nesting
- A module may instantiate other modules.
- `inst` supports both component targets and module targets.

### Rule 1.2: Boundary Access
- Parent modules must connect to child modules through child ports or exposed interfaces.
- Direct reference to child-local private nets is disallowed by default.

### Rule 1.3: Encapsulation Integrity
- Child module boundary is a semantic contract.
- Breaking boundary access requires explicit future extension policy and is not default behavior in v0.1.

## 2. Connect Semantics
### Rule 2.1: Supported Modes
- SDL supports:
  - pin <-> net
  - pin <-> pin
  - interface <-> interface
  - fanout/batch endpoint connection

### Rule 2.2: Interface Matching
- Interface-to-interface connect may auto-match by member name when types are compatible.
- If member names differ, explicit `map` statements are required.

### Rule 2.3: Endpoint Resolution
- Every endpoint in `connect`, `net`, `tie`, `topology`, and `map` must resolve to a valid RefPath.

## 3. Topology Semantics
### Rule 3.1: Topology Is Additive
- `topology` adds ordered path intent and does not replace `net` connectivity.

### Rule 3.2: Typical Use
- USB protection chains, analog front-end chains, and clock distribution paths are expected topology use cases.

### Rule 3.3: Topology Coherence
- Endpoints declared in topology must be compatible with underlying connectivity intent.

## 4. Constraint vs Requirement
### Rule 4.1: Constrain
- `constrain` describes object properties, preferences, or bounded rules that tools can evaluate.

### Rule 4.2: Require
- `require` describes engineering obligations that must be satisfied.
- Examples: decoupling, protection, pullup, return_path_required.

### Rule 4.3: Separation
- Do not encode pure requirement obligations as only raw constraints without requirement semantics.

## 5. Power Domain Semantics
### Rule 5.1: Domain Object Meaning
- `domain` is a semantic power object, not only a net label.

### Rule 5.2: Minimum Domain Structure
- Domain semantics must distinguish:
  - source
  - return
  - provider
  - consumers

### Rule 5.3: Connectivity and Domain Consistency
- Power-related connects/nets should be consistent with declared domain semantics.

## 6. Placement Hint Semantics
### Rule 6.1: Non-Geometry Nature
- `place` is a hint and not a final geometry coordinate system.

### Rule 6.2: Downstream Use
- Placement hints are consumed by schematic/layout generation stages as intent inputs.

## 7. Completeness Check Minimum Set
The minimum completeness checks must cover:
- reference legality
- duplicate naming checks
- interface completeness
- requirement satisfaction
- power domain rationality
- topology legality
- external connector protection obligations

## 8. Determinism and Normalization
- Equivalent designs should normalize to stable ordering and reference forms.
- Non-semantic formatting differences must not change semantic interpretation.
- Diagnostics should target stable RefPath locations.
