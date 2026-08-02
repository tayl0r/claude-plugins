# The dev-flow pipelines are flat — the orchestrator is the only spawner

Both pipelines spawn only leaf subagents. The orchestrator invokes every fan-out skill (`adversarial-review`, `subagent-driven-development`) in-context and spawns those skills' workers itself; no spawned subagent spawns anything. `dev-flow` 1.1.0 was nested — the orchestrator spawned a stage subagent, which invoked `adversarial-review`, which spawned reviewers — and 1.2.0 flattened it.

The trigger for flattening was a harness capability change, but the capability is not what keeps the pipeline flat. Whether a spawned subagent holds the `Agent` tool has oscillated: **2.1.217** granted it, and 1.1.0 was developed and verified against that; **2.1.218** withdrew it, which is why 1.2.0 flattened; **2.1.220** restored it, measured 2026-08-02 by asking a spawned `general-purpose` subagent to enumerate its own tool list. A design premised on either state is wrong within a few patch releases, and no check in this repository can detect the flip.

What holds independently of any version is that flattening put three properties in the orchestrator's own hands.

- **Provenance is read, not relayed.** The orchestrator reads each review's returned provenance line directly and halts if it is missing or its tiers are wrong. Nested, it would instead read a stage subagent's *summary* of that line — a relayed claim from an agent with an interest in reporting success. ADR-0002 records that this line is the only mechanical evidence that "Review integrity (never inline)" was honoured; relaying it downgrades the evidence to hearsay.
- **Resume state has one owner.** Every resume decision is a mechanical read of the branch tip or the PR, and the orchestrator holds the fan-out controllers' loops — the review's group loop, SDD's task loop — directly. A controller loop inside a spawned subagent keeps its position in a context the orchestrator cannot see and a crash cannot recover; it is on no branch tip and in no PR.
- **It works on every version**, including both sides of a capability that has now flipped twice.

The runtime guard against a harness without nesting is not this decision and never was. It is `adversarial-review`'s **Review integrity (never inline)** clause (`plugins/*/skills/adversarial-review/SKILL.md`): the seed and resolver passes MUST run as separate subagents, and if they cannot be spawned — no `Agent` tool, or a required model unavailable — the review halts and reports rather than silently substituting a single-model inline pass. That fires on the capability actually observed, whatever the version, and needs no prose predicting which version is in use. Flat topology means the clause never has to fire for want of spawn depth. Neither depends on the other.

Consequently the pipelines' `SKILL.md` copies state the rule and a version-independent reason for it, and name no harness version at all. The dated evidence lives here, where a dated record is the correct form: "as of 2.1.218 nesting was unavailable" is true forever in an ADR and false eventually in an operating instruction.

## Considered options

- **Nested topology behind a capability gate** (`dev-flow` 1.1.0) — rejected in 1.2.0 and not revived. The gate halted loudly rather than degrading silently, which is correct, but a loud halt is still no run: 1.1.0 could not execute at all on 2.1.218. Nesting also makes the provenance check hearsay and the controller loops unresumable, so its isolation benefit is paid for on every version and delivered on only some.
- **Track the harness version in the pipeline `SKILL.md` prose and update it when it changes** — rejected: nothing in this repository can notice the number going stale, and it went stale twice before anyone did. A claim no check can verify is a claim that will eventually be wrong while still being read as authoritative.
- **Re-nest now that 2.1.220 restores the capability** — rejected: the two reasons that are actually load-bearing (provenance, resume ownership) are untouched by the restoration, so re-nesting would trade a working design for one that is a patch release away from failing again, and would give up a property the pipeline's own contract depends on.
- **Env-var stopgap** (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`) — rejected at flatten time and still rejected: a per-machine flag makes the pipeline's topology a function of local configuration.

## Consequences

The orchestrator's context carries fan-out controller state for the whole of a run — state that nesting would have isolated in a child context. This is bounded deliberately: every leaf returns a short summary, every handoff is a file, and the run is recoverable via resume. That bound is what makes the trade acceptable rather than free, and it is the first thing to re-measure if runs start exhausting orchestrator context.

## Revisit when

The harness grants nested spawning as a *contract* rather than a per-release behaviour — and even then, only if a nested review's provenance line and a nested controller's loop position can still be read by the orchestrator without a relay. Absent both, the restoration of the capability is not a reason to revisit.
