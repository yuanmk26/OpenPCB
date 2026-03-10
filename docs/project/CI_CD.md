# OpenPCB CI/CD Baseline (v1)

## 1. Goals

- CI: block low-quality changes before merge and keep the main branch healthy.
- CD: planned for the next phase, after CI is stable.

## 2. Triggers

- Pull request: run full CI gates.
- Push to `main`: run full CI gates.
- Tag-based release is not enabled yet in v1.

## 3. CI Quality Gates

- `ruff check .`
- `python -m pytest`
- `python -m build`

## 4. CD Release Strategy (Planned)

- Planned target: tag-driven GitHub Release (`v*`) with `dist/*` artifacts.
- Current status: not implemented in repository workflows.
- v1 does not publish to PyPI.

## 5. Failure Handling

- CI failure: block merge until fixed and rerun.
- CD policy is documented but execution workflow will be added later.

## 6. Roles

- Contributors: run `ruff + pytest + build` locally before pushing.
- Maintainers: maintain CI workflows now; add release permissions when CD starts.

## 7. TODO Alignment

Recommended TODO milestone:
- I1: CI workflow for PR/main.
- I2: CD workflow for tag release (planned, not implemented yet).
- I3: CI/CD policy documentation and maintenance.
