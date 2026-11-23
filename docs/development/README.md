# Development guide

Start with the [member guide](member-guide.md) for Stages 00–24.
[ADR 003](../architecture/003-separate-backend-services.md) is the current service
architecture and supersedes the single-backend portions of the older design.

| Artifact | Purpose |
|---|---|
| [Progress](progress.md) | Actual stage status and verification limits |
| [Work board](work-board.csv) | 41 requirement stories, ownership, expected behavior and evidence |
| [Decision register](decision-register.md) | Selected defaults, open external inputs and release gates |
| [State review](state-transition-review.md) | Critical transactional transitions before schema implementation |
| [Repository review](repository-review.md) | Original source review plus restructuring follow-up |
| [File inventory](file-inventory.csv) | Reviewed files and responsibilities |
| [Traceability](../testing/requirements-traceability.csv) | Requirements to stages, modules, services and proposed tests |
| [Stage 00 evidence](../testing/evidence/stage-00.md) | Executed static planning checks |
| [Evidence template](../testing/stage-evidence-template.md) | Reproducible later stage runs |

Stories remain PLANNED until implemented and verified. Proposed test names are
acceptance targets, not claims that those tests exist or pass.
