# claude-plugins

A marketplace of Claude Code plugins. Its centre of gravity is `dev-flow`, a pipeline that carries a change from design through plan, execution, and review to a merged PR, and `adversarial-review`, the two-tier review protocol every dev-flow stage runs.

## Language

### The review protocol

**Seed**:
A findings-only reviewer in the first tier. It reads and reports; it never edits, judges, or decides.
_Avoid_: finder, first-pass reviewer

**Resolver**:
A reviewer in the second tier, which weighs grouped seed findings against the design rubric and decides what changes.
_Avoid_: group agent, judge, arbiter

**Tier**:
The model class a reviewer is spawned on — `sonnet` for seeds, `opus` for resolvers. Distinct from *family*.

**Family**:
A model's product line (Opus, Sonnet, Fable), independent of any dated version within it.

**Family match**:
The check that a reviewer's self-reported model belongs to the family its requested tier names. Preferred over matching a dated model id, which drifts.

**Provenance**:
The line a review returns stating how many reviewers it actually spawned per tier. Evidence of fan-out and tier conformance — never of model diversity.

**Angle**:
One lens in the diff-mode quality seed's list: reuse, simplification, efficiency, altitude, seam placement.

**Pass**:
A named, self-contained check a seed runs over an artifact, carrying its own trigger and stopping conditions. An angle is a lens *within* a seed's list; a pass is a whole check.

**Trigger**:
The precondition deciding whether a pass or angle applies to a given artifact at all. A check without one runs on everything and manufactures false positives.

**Reportability rule**:
The bar a candidate finding must clear before a seed may state it. Where a trigger narrows *which artifacts get asked*, a reportability rule narrows *what may be said*.

**Design rubric**:
The nine-bullet statement of what "best long-term design" means. Both the design/plan quality seed's lens and every resolver's judgment criteria in all three modes, making it the widest-broadcast text in the skill.

### The pipeline

**Artifact**:
The single thing one review runs against — a design doc, a plan doc, or a branch diff. Each corresponds to one *mode*.

**Stop**:
A boundary where the pipeline halts and hands control back: `post-design`, `post-plan`, or `pre-merge`.

**Slug**:
The short, opaque, immutable identifier for one pipeline run, threading its branch, its document filenames, and its PR. Renaming a feature changes prose, never the slug.

### Duplication

**Mirror pair**:
Two files required to stay line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, enforced mechanically by `scripts/check-sync.py`.

**Hand-mirrored pair**:
Two files that must be kept in step by hand because no mechanical check can cover them. Divergence here is silent, which is why changes touching one carry their own greps.

### Cross-cutting

**Seam** _(Michael Feathers)_:
A place where behaviour can be altered without editing in that place. This repo uses the word at two levels: *protocol seams* in the pipeline's own design, such as a declared preference a delegated skill reads instead of prompting; and *code seams* in a change under review.
_Avoid_: boundary
