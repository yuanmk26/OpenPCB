# Directory Tree (Current Snapshot)

This document records the current repository structure and the architecture-document landing points for the agent-team redesign.

## Top-level directories

```text
openpcb/
  data/
  docs/
  examples/
  scripts/
  src/
  tests/
```

## Top-level files

```text
AGENTS.md
README.md
LICENSE
pyproject.toml
pytest.ini
project.json
openpcb_task_breakdown.md
```

## docs/ structure (current)

```text
docs/
  architecture/
    README.md
    system-architecture.md
    agent-architecture.md
    mode-action-architecture.md
    pcb-pipeline-architecture.md
    directory_tree.md
  changes/
  gui/
  project/
    README.md
    TODO.md
    CI_CD.md
    knowledge-base.md
  sdl/
```

## src/ structure (current)

```text
src/
  openpcb/
    app/
    agent/
    config/
    domain/
    infra/
    schema/
    utils/
  gui/
    ui/
    src-tauri/
```

## Architecture-document landing points for this redesign

- `docs/architecture/agent-architecture.md`: defines `pi-mono + agent-team` orchestration and role boundaries.
- `docs/architecture/system-architecture.md`: places agent-team flow in end-to-end system architecture.
- `docs/project/knowledge-base.md`: project information base maintained by `Project-Info Agent`.

## Maintenance notes

- Keep this file aligned with actual repository paths.
- Avoid historical or inferred directory entries that do not exist in the repository.
- If structure changes, update this file and add a same-day record under `docs/changes/<YYYY-MM-DD>/`.
