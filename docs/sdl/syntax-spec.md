# SDL Syntax Specification (Draft)

## Purpose
This document describes the draft Block DSL syntax for `.opsdl` files.
It is intentionally compact and may evolve in later versions.

## Lexical Conventions
- UTF-8 text.
- Line comments start with `#`.
- Identifiers use `[A-Za-z_][A-Za-z0-9_-]*`.
- String literals use double quotes.
- Object blocks use `{ ... }`.

## Top-Level Structure
A file contains one primary `module` block.

Example sketch:
```text
module "<name>" {
  version "0.1"
  ...
}
```

## Block Forms
Common block patterns in this draft:
- `meta { key "value" }`
- `component "<id>" { ... }`
- `port "<name>" { ... }`
- `net "<name>" { connect ["A.B", "C.D"] }`
- `constraint "<id>" { target "..."; rule "..."; value "..." }`

## Property Forms
- Scalar: `key "value"` or `key 123`
- List: `key ["v1", "v2"]`
- Nested block: `key { ... }`

## Reserved Keywords
`module`, `version`, `meta`, `params`, `component`, `pin`, `port`, `net`, `connect`, `constraint`, `variant`, `use`, `include`.

## Grammar Notes
- This draft does not define full EBNF.
- Whitespace is non-semantic outside strings.
- Unknown keys are allowed only when validation profile permits extension.
