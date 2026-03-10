# OpenPCB CI/CD Baseline (v1)

## 1. Goals

- CI: block low-quality changes before merge and keep the main branch healthy.
- CD: publish build artifacts to GitHub Release from version tags.

## 2. Triggers

- Pull request: run full CI gates.
- Push to `main`: run full CI gates.
- Push tag `v*`: run release workflow.

## 3. CI Quality Gates

- `ruff check .`
- `python -m pytest`
- `python -m build`

## 4. CD Release Strategy

- Tag-driven release with pattern `v*`.
- Build sdist and wheel from source.
- Create or update GitHub Release for the tag.
- Upload `dist/*` artifacts to the release.
- v1 does not publish to PyPI.

## 5. Failure Handling

- CI failure: block merge until fixed and rerun.
- CD failure: keep logs, fix root cause, and rerun via tag workflow.
- Post-release issues: ship a new version tag instead of overwriting artifacts.

## 6. Roles

- Contributors: run `ruff + pytest + build` locally before pushing.
- Maintainers: maintain workflows and release permissions.

## 7. TODO Alignment

Recommended TODO milestone:
- I1: CI workflow for PR/main.
- I2: CD workflow for tag release.
- I3: CI/CD policy documentation and maintenance.
