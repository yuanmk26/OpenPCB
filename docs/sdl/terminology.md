# SDL Terminology

## Purpose
This glossary defines canonical terms for OpenPCB SDL v0.1.
When wording conflicts across documents, this glossary has priority.

## Core Positioning Terms
- **Authoritative Description**: SDL text as the canonical design source.
- **Derived Runtime Structure**: in-memory normalized representation produced from SDL for tools.
- **Engineering DSL**: statement-oriented, human-reviewable language for design intent.

## Structural Terms
- **Module**: top-level reusable design unit; may instantiate components or other modules.
- **Component**: library/type entity describing a part kind referenced by instances.
- **Instance (`inst`)**: concrete usage of a component or module.
- **Pin**: instance connection point.
- **Port**: module boundary connection point.
- **Interface**: structured, named set of members (for example SWD, I2C, USB2).
- **Interface Member**: typed signal item inside an interface.
- **Group**: logical collection for organization or constraints, not an electrical net by itself.

## Connectivity Terms
- **Net**: logical connectivity equivalence class.
- **Connect**: explicit connection statement between endpoints.
- **Expose**: export internal instance endpoint/interface to module boundary.
- **Tie**: explicit identity/equivalence binding between named endpoints or nets.
- **Topology**: ordered path semantics layered on top of connectivity.
- **Mapping (`map`)**: explicit correspondence when interface/member naming differs.
- **Bus/Vector**: homogeneous indexed signal collection.

## Engineering Semantics Terms
- **Electrical Type**: electrical behavior class for pins/ports/interface members.
- **Role**: engineering role label, such as `mcu`, `regulator`, `protection`, `external_connector`.
- **Power Domain**: semantic power object with source/return/provider/consumers.
- **Signal Class**: implementation-oriented signal category (`power`, `ground`, `clock`, `reset`, `diffpair`, `analog_sensitive`).
- **Connector Category**: external connector semantic category.

## Constraint and Validation Terms
- **Constraint (`constrain`)**: machine-checkable rule or preference.
- **Requirement (`require`)**: engineering obligation that must be satisfied.
- **Placement Hint (`place`)**: non-geometric implementation hint for downstream layout/schematic stages.
- **Completeness Check**: validation set ensuring references, interfaces, requirements, domains, topology, and protection obligations are coherent.
- **RefPath**: stable hierarchical reference path (for example `u_mcu.power.vdd[0]`).

## Agent Operation Terms
- **Patch Operation**: structured local edit action on SDL-derived runtime structure.
- **Roundtrip**: parse SDL, apply patches, validate, and write back SDL with preserved semantics.
