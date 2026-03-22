# SDL Object Dictionary

## Purpose
This dictionary defines first-draft SDL object types and required fields.
It is a semantic contract, not an implementation schema.

## Module
Required fields:
- `name`: unique module identifier.
- `version`: module document version.

Common optional fields:
- `meta`: author, project, tags.
- `params`: parameter set used by instances or constraints.

## Component
Required fields:
- `id`: stable object id.
- `ref`: reference designator (for example `U1`, `C4`).
- `type`: logical part category.

Common optional fields:
- `value`: human-readable value.
- `footprint`: layout package hint.
- `pins`: explicit pin map for symbolic connectivity.

## Pin
Required fields:
- `name`: pin identifier inside component scope.

Common optional fields:
- `function`: semantic role such as `power_in`, `gpio`, `analog_in`.
- `electrical`: electrical type classification.

## Port
Required fields:
- `name`: module-level external interface name.
- `dir`: direction (`in`, `out`, `inout`, `passive`).

Common optional fields:
- `domain`: signal domain hint (`power`, `digital`, `analog`).

## Net
Required fields:
- `name`: net identifier.
- `connect`: list of endpoints (`ref.pin` or `port:name`).

Common optional fields:
- `class`: routing class hint.
- `voltage`: nominal voltage metadata.

## Constraint
Required fields:
- `id`: stable constraint identifier.
- `target`: object reference or selector.
- `rule`: rule key string.

Common optional fields:
- `value`: parameterized rule value.
- `severity`: `error` or `warning`.

## Variant
Required fields:
- `name`: variant id.
- `changes`: list of controlled modifications.

## Stability Notes
- Required fields are the minimum contract for this draft.
- Additional fields are allowed if documented and validated consistently.
