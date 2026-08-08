# claude-plugins

A marketplace of Claude Code plugins. Its centre of gravity is `dev-flow`, a pipeline that carries a change from design through plan, execution, and review to a merged PR, and `adversarial-review`, the two-tier review protocol every dev-flow stage runs.

## Language

### The review protocol

**Seed**:
A findings-only reviewer in the first tier. It reads and reports; it never edits, judges, or decides.
_Avoid_: finder, first-pass reviewer

**Resolver**:
A reviewer in the second tier, which weighs grouped seed findings against the design rubric and decides what changes.
_Avoid_: group agent, group-resolution agent, judge, arbiter

**Tier**:
The model a pinned agent is spawned on — `claude-sonnet-4-6` for seeds, `claude-opus-4-8` for resolvers, the produce-subagent, and the risky-task reviewer. Pinned by dated id in an *agent definition* rather than by family alias, so that a new release in either family cannot silently re-point a tier. Distinct from *family*.

**Agent definition**:
A `plugins/<plugin>/agents/<agent>.md` file whose frontmatter pins a spawnable `subagent_type` to a dated model id. The only place a dated id can be requested *when spawning a subagent* — the `Agent` tool's `model` parameter takes family aliases only, and passing it overrides the pin. The session's own model is a separate surface, where `claude --model` does accept a full id. Distributed by the plugin system like a skill, and registered under the plugin-qualified name `<plugin>:<name>` — the bare name does not resolve.
_Avoid_: subagent file, agent template

**Family**:
A model's product line (Opus, Sonnet, Fable), independent of any dated version within it. A plugin's product line likewise: `dev-flow` is the family name its two variants share, independent of either variant's own version. A set of merely related constructs (connectors, handlers, jobs…) is not a family — the word for that is *kind*.

**Tier match**:
The check that a reviewer's self-reported model is the dated id its tier pins, ignoring any variant suffix the harness appends (`claude-opus-4-8[1m]` matches `claude-opus-4-8`).
_Avoid_: family match (the name from when tiers were named by alias)

**Provenance**:
The line a review returns stating how many reviewers it actually spawned per tier, and the normalized dated id each one matched to. Evidence of fan-out and tier conformance — never of model diversity.

**Angle**:
One lens in the diff-mode quality seed's list: reuse, simplification, efficiency, altitude, seam placement, glossary conformance.

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

### Topology

**Orchestrator**:
The agent that drives one pipeline run from stage to stage, and the run's only *spawner* — the one agent that spawns any other; every other agent in the run is a leaf.

**Leaf**:
A spawned subagent that spawns nothing itself: a produce-subagent, one of a review's seeds or resolvers, one of SDD's implementers or fixers.

**Fan-out**:
One agent dispatching N workers and holding their loop — a review's seeds and resolvers, SDD's implementers. That agent is the fan-out's *controller*, and in both pipelines it is always the orchestrator, which is why fanning out adds no level.

**Flat topology**:
The property that every spawn in a run is one level deep: the orchestrator spawns leaves, and nothing else spawns at all. *Topology* alone names this axis — which agent may spawn which — and nothing else here. Required rather than preferred, for reasons independent of any harness version (ADR-0003).

### Duplication

**Mirror pair**:
Two files required to stay line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, enforced mechanically by `scripts/check-sync.py`.

**Hand-mirrored pair**:
Two files that must be kept in step by hand because no mechanical check can cover them. Divergence here is silent, which is why changes touching one carry their own greps.

### Cross-cutting

**Seam** _(Michael Feathers)_:
A place where behaviour can be altered without editing in that place. This repo uses the word at two levels: *protocol seams* in the pipeline's own design, such as a declared preference a delegated skill reads instead of prompting; and *code seams* in a change under review.
_Avoid_: boundary
