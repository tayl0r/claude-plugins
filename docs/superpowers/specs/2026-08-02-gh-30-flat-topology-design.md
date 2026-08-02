---
dev-flow:
  slug: gh-30-flat-topology
  stops: [pre-merge]
  docs: commit
---

# gh-30: re-anchor the flat-topology bullet to a reason no harness release can falsify, and record the decision in an ADR

## Goal

Close issue #30. The flat-topology bullet in both pipeline `SKILL.md`s asserts as present-tense fact that Claude Code does not grant spawned subagents the `Agent` tool. That is **false on 2.1.220** — the capability was present on 2.1.217, withdrawn on 2.1.218, and restored on 2.1.220.

Three things ship:

1. Both copies of the bullet are rewritten so that **no harness version and no tool name appear in shipped text**, and the normative clause (`This is required, not a preference:`) is re-attached to a reason no harness release can falsify plus the instruction that follows from it.
2. `docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md` records the decision — why the pipelines are flat, the 217→218→220 oscillation as dated evidence, and where the runtime guard actually lives.
3. `dev-flow` 2.6.0 → **2.7.0**, `dev-flow-worktree` 1.8.0 → **1.9.0**.

No stage, contract, or interface moves, and the topology is not revisited (see B below — it survives, and on better grounds than the ones written down). What *does* move is what the shipped bullet is able to enforce: see C, and the bump rationale in §5.

## Scope check — one subsystem, no decomposition

One decision, expressed in one bullet duplicated across a hand-mirrored pair, plus the durable record of that decision, plus the two version bumps that make the edit reach the version-keyed cache. The ADR and the bullet are not independent subsystems: the ADR exists *because* the bullet stops carrying the rationale. Nothing here decomposes.

### Hard scope constraints

**In scope:** `plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, `docs/adr/`, and the two `plugin.json` version bumps.

**Forbidden — must not be edited:** `plugins/*/skills/adversarial-review/SKILL.md` (a concurrent change owns it), `CLAUDE.md`, `scripts/`, `CONTEXT.md`. Nothing designed here requires any of them; `adversarial-review/SKILL.md:18` is *quoted* by the ADR and left byte-identical. If implementation appears to need one of these files, that is a blocker to report, not to work around. Verification step 3 re-copies the same fenced-block reader as the four designs before it; that duplication, and whether `CLAUDE.md`'s *"there is no shared runner to call"* still holds, are **#24**, which owns both files. Not re-litigated here.

**Out of scope:** `docs/superpowers/` artifacts that mention 2.1.218 (`2026-07-20-dev-flow-design.md`, `2026-07-22-dev-flow-flatten-design.md`, `2026-07-22-dev-flow-nested-review-fix-design.md`, `2026-07-27-gh-7-review-depth-design.md`, and two plans). They are dated historical records, and both shipped review checks skip that path by construction. Correcting them would falsify the record.

Stop is `pre-merge`. No merge.

---

## A. Is an ADR warranted at all?

**Yes.** One line: *the deletion removes the last durable answer to "why is this pipeline flat?", and the only other record of that answer — `docs/superpowers/specs/2026-07-22-dev-flow-flatten-design.md` — states a reason that is now false, so a contributor who tests the premise reaches the wrong conclusion. Issue #30 is that mistake, already happening.*

The case against is real and worth stating: git history holds the removed text, and a whole ADR for one deleted paragraph is over-production. It loses on two facts.

**The surviving alternative record is actively misleading, not merely absent.** `2026-07-22-dev-flow-flatten-design.md` opens with *"Nested subagent spawning was removed in Claude Code 2.1.218 … so the nested topology cannot run"* and *"the 'nesting is available' premise is false on current and future versions."* That is the whole recorded rationale for flattening, it is a prediction, and the prediction failed within three patch releases. A contributor who finds that document, re-runs the probe, and observes nesting working has been handed an argument for re-nesting — which is exactly the reasoning path that produced #30's own first (superseded) proposal. Git history is a worse home for the same reason: `git log -S` surfaces the *false* sentence, and a blame trail through a superseded design is not a decision record.

**ADRs here are read, not shelved.** `docs/agents/domain.md` instructs engineering skills to read `docs/adr/` *before* working in an area, and ADR-0001 is itself a decision about this exact pair of pipeline files. The discovery path is designed and already exercised.

**The apparent tension with the gh-26 precedent is not one.** That design rejected an ADR for a *vocabulary* fact, because *"neither shipped check reads `docs/adr/`"* — the consumer there was a `sonnet` seed grepping `CONTEXT.md`. The consumer here is a contributor or agent exploring the pipeline's topology, and `docs/agents/domain.md` points that consumer at `docs/adr/` by name. Different consumer, different home; the precedent is followed, not contradicted.

**Not `CONTEXT.md`.** This is a decision with consequences and a revisit condition, not a term. `CONTEXT.md` defines shapes; ADRs record choices.

---

## B. Does the conclusion survive the premise being false?

**Yes — and the version fact was never the strongest reason.** Tested, not assumed: three version-independent justifications are already load-bearing in the pipeline design, each written down in `Cross-Cutting Concerns` today.

**1. Provenance is read, not relayed.** *"The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line … directly and halts if it is missing or its tiers violate `adversarial-review`'s Model section."* The word doing the work is **directly**. Under a nested topology the orchestrator reads a *stage subagent's summary* of that line — a relayed claim from an agent with an interest in reporting success. ADR-0002 already establishes that this line is *"the only mechanical evidence that 'Review integrity (never inline)' was honoured"*; nesting downgrades that evidence to hearsay. This reason has nothing to do with any harness version.

**2. Resume state has one owner.** *"Idempotent resume: guaranteed by the Artifact Contract — every resume decision is a mechanical read of the branch tip or the PR"*, and *"the orchestrator holds the fan-out controllers' state directly (the review's group loop, SDD's task loop)."* A controller loop running inside a spawned subagent keeps its state in a context the orchestrator cannot see and a crash cannot recover — the loop position is on no branch tip and in no PR. Flat topology is what makes the Artifact Contract's guarantee true rather than aspirational.

**3. Loud failure is not the same as a working pipeline.** `adversarial-review`'s Review-integrity clause halts if reviewers cannot be spawned, so a nested design on a no-nesting harness fails *loudly*. That is correct behaviour and it is not a defence of nesting: it still fails. The 1.1.0 → 1.2.0 history is the proof — 1.1.0's capability gate worked exactly as designed and the pipeline could not run.

The honest cost of flat, stated so the trade is visible: the orchestrator's context carries fan-out controller state for the whole run, which nesting would have isolated. `Context hygiene` bounds it deliberately — every leaf returns a short summary, every handoff is a file — and that bound is what makes the trade acceptable rather than free.

**Verdict: flat topology stands.** Nothing to report as a design defect, and no re-architecture is proposed or implied. The defect is confined to the *written justification*: it named a version-dated fact as the reason when three durable reasons were sitting one section below in the same file.

---

## C. Does deleting the text lose anything a reader or model needs at runtime?

The issue comment's fragment 1 is 208 chars and **begins with `This is required, not a preference: `**. Deleting both fragments verbatim is not hypothetical — applied literally it yields a 336-char bullet reading:

```text
- **Flat topology — the orchestrator is the only spawner.** Every subagent dev-flow spawns is a leaf; no subagent spawns a subagent. So the orchestrator invokes every fan-out skill (`dev-flow:adversarial-review`, `subagent-driven-development`) in-context and spawns their worker leaves itself — always one level, works on every version.
```

That is grammatical and true. Within the bullet it is also **purely descriptive**: every clause states what the pipeline does, none states that an orchestrator may not do otherwise.

**What the file still says without it — checked, not assumed.** The prohibition does not rest on this bullet. The rest of each `SKILL.md` carries it operatively at six sites: the preamble `:8`; *"The orchestrator runs the fan-out skills — `adversarial-review` and `subagent-driven-development` — itself, in-context"* (`:50` / `:49`); the Pipeline preamble `:201` / `:195`; the three per-stage *"invokes … in-context"* review calls; Stage 3's *"No execute-stage-subagent wrapper"* (`:225` / `:219`), which forbids the deviation by name; and `Review provenance is checked, not assumed`, which says the orchestrator reads the line *directly*. An orchestrator that nested would be overriding explicit instructions, not filling a silence. So the case for keeping the clause is **not** that deletion leaves the bullet toothless — that case is false, and this design does not make it.

**The gap that is real.** All six sites state the rule *flatly*, as what this pipeline does. None of them says what to conclude on observing that the harness now permits otherwise — and until 2.1.220 none had to, because a nested dispatch found no `Agent` tool in its leaves and the constraint was enforced by the environment. That inference is now reachable, and #30's own superseded first proposal is it already being drawn by a reader holding the same facts. It also fails *silently*: a wrapped stage returns a **relayed** provenance line, which `Review provenance is checked, not assumed` consumes as if it were direct, and nothing in the repo detects the difference. One sentence of insurance against an undetectable failure of the pipeline's only mechanical review-integrity evidence is the trade being made here, and it is the whole of it.

**The comment's claim that "works on every version" carries the durable reason is half right.** Those five words are a durable *benefit claim*, and the same claim already appears at `SKILL.md:8` in both files (*"the only agent that spawns — so the multi-agent review and the Execute loop work on any Claude Code version"*) — so the bullet is not its only carrier and losing it there costs little. What the bullet uniquely carries is not the prohibition — six operative sites carry that — but its **modality**: that the rule does not follow from, and is not contingent on, what the harness currently allows.

**Decision: keep `This is required, not a preference:` and re-attach it to a reason no harness release can falsify.** The replacement states the instability and then the rule that follows from it:

> whether a spawned subagent can itself spawn is a harness capability that has been withdrawn and restored across patch releases, and observing that it currently works is not permission to nest

The discriminator against the text being replaced is precise, and it is the test any future edit here should apply. **The old clause was present tense about a capability** (*"does not grant"*), so an upgrade falsifies it; **the new clause is past-perfect about history** (*"has been withdrawn and restored"*), so an upgrade can only add to it. It names no version, so there is no number to update — and no tool: `Agent` is deliberately absent, because #30's own probe already hedges the name (*"a tool named `Agent` or `Task`"*), and a renamed or restructured spawn capability would strand the sentence on that second axis. The clause's second half is an instruction rather than a claim, so nothing can falsify it at all. Between them the sentence is inert to every axis a harness release has been observed to move — version number, tool name, and capability state — which is the actual defect #30 identifies.

### Alternatives considered

- **Delete both fragments verbatim, as the comment specifies.** Rejected, but narrowly: it does not leave the pipeline undefended — six operative sites survive — it deletes the only text telling an orchestrator that observing nesting to work is not permission to use it, at the exact release where that observation became possible. Everything else in the comment is adopted: no versions in shipped text, the history goes to an ADR, the runtime guard is `adversarial-review`'s clause.
- **Update the version number and invert the claim** (the issue body's *"argue past this first"* option). Rejected twice over: it goes stale on the next flip with nothing in the repo able to notice, and on 2.1.220 the corrected fact says nesting *is* available — an argument *for* nesting sitting inside the bullet forbidding it.
- **Delete the fragments and add the ADR pointer to the bullet** (`see docs/adr/0003-…`). Rejected: the orchestrator never acts on a pointer, `SKILL.md` ships whole into every invocation, and `docs/agents/domain.md` already routes contributors to `docs/adr/` before they work in an area. Adding ~110 chars of contributor-facing navigation to shipped text is the shape `CLAUDE.md` keeps out of `SKILL.md`.
- **Move `required` to the end** (*"always one level — required, not a preference, because it works on every version"*). Rejected: it reads as a benefit rather than a constraint, and it separates the imperative from the sentence stating what is forbidden.
- **Restate the provenance and resume reasons in the bullet.** Rejected: they are already written, in full, two sections below in the same file. Restating them costs tokens in every invocation to duplicate text the same reader already has, and creates a fourth copy to keep in step across a hand-mirrored pair.
- **Move the imperative to the Pipeline preamble** (`:201` / `:195`), where the operative instructions live. Rejected: the preamble already states the rule in operative form, so what would move there is the modality alone — a fourth copy of the same idea on a hand-mirrored pair, rejected just above for the same reason. It also turns a one-line replacement into a two-line edit per file, giving up the length-invariance the conformance check leans on. And the *reason* — that the harness capability is unstable — is genuinely an environment assumption, so `## Environment Assumptions` is its correct section.

### The token argument, honestly

The comment's version saves 322 chars per file; this one saves 93 (658 → 565 in `dev-flow`, 676 → 583 in `dev-flow-worktree`). The 229-char difference is the normative clause and its reason — roughly 57 tokens per invocation, deliberately spent. As the comment itself says, the token argument is the weakest of the three: the change earns its place because the text is **false** and **unmaintainable**, and both of those are fully repaired here.

---

## Exact change list

### 1. `plugins/dev-flow/skills/dev-flow/SKILL.md` — replace line 266

Replace the whole line (the first bullet under `## Environment Assumptions`) with:

```
- **Flat topology — the orchestrator is the only spawner.** Every subagent dev-flow spawns is a leaf; no subagent spawns a subagent. This is required, not a preference: whether a spawned subagent can itself spawn is a harness capability that has been withdrawn and restored across patch releases, and observing that it currently works is not permission to nest. So the orchestrator invokes every fan-out skill (`dev-flow:adversarial-review`, `subagent-driven-development`) in-context and spawns their worker leaves itself — always one level, works on every version.
```

### 2. `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — replace line 261

Replace the whole line (the first bullet under `## Environment Assumptions`) with:

```
- **Flat topology — the orchestrator is the only spawner.** Every subagent dev-flow-worktree spawns is a leaf; no subagent spawns a subagent. This is required, not a preference: whether a spawned subagent can itself spawn is a harness capability that has been withdrawn and restored across patch releases, and observing that it currently works is not permission to nest. So the orchestrator invokes every fan-out skill (`dev-flow-worktree:adversarial-review`, `subagent-driven-development`) in-context and spawns their worker leaves itself — always one level, works on every version.
```

Both are **one-line replacements**: `dev-flow/skills/dev-flow/SKILL.md` stays at **277** lines, `dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` at **271**. The two blocks differ only in the plugin/skill name — substituting `dev-flow-worktree` → `dev-flow` in block 2 yields block 1 exactly, and Verification asserts that.

### 3. Phrases the change removes

Exact substrings that must appear **nowhere under `plugins/`** afterwards:

```text
**Claude Code 2.1.218 does not grant spawned subagents the `Agent` tool** (nested spawning was removed; the harness's recommended pattern is top-level orchestration only).
(Nesting worked on 2.1.217 and was relied on by this plugin's 1.1.0; the 2.1.218 removal is why 1.2.0 flattened.)
2.1.218
2.1.217
```

`2.1.218` / `2.1.217` are the broader net: today `grep -rn "2\.1\.2" plugins/` returns exactly the two lines being replaced, so after the change it must return nothing at all. This design doc and the new ADR both quote these strings, which is why every residue grep is scoped to `plugins/`.

### 4. New file — `docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md`

Full contents:

```
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
```

### 5. Version bumps

| Plugin | From | To |
|---|---|---|
| `dev-flow` | 2.6.0 | **2.7.0** |
| `dev-flow-worktree` | 1.8.0 | **1.9.0** |

**Minor, one line:** shipped `SKILL.md` text changes, so the version-keyed cache must see it. Minor rather than patch, on two grounds. **It is not a cosmetic rewrite:** the replacement clause's second half — *"observing that it currently works is not permission to nest"* — is an instruction the bullet did not previously carry, addressed to the running orchestrator and closing the inference C shows is now reachable. That is a behaviour change on `CLAUDE.md`'s own terms (*"bump `version` … on any behavior change"*). **And no non-zero patch segment has ever existed here:** of the fifteen bumps in this repo's history, fourteen are minor and one is the major that accompanied the plugin split. Introducing a second bump size would establish a repo-wide convention as a side effect of a documentation fix — in a change whose scope forbids editing `CLAUDE.md`, the only place that convention could be recorded. If a patch/minor discipline is wanted, it should be decided deliberately, as its own change — filed as **#33**.

`description` in neither `plugin.json` changes, so `check-sync.py`'s manifest check is unaffected and `.claude-plugin/marketplace.json` is untouched.

---

## Assumptions recorded

- **Both plugins are at 2.6.0 / 1.8.0 at implementation time.** Verified on this branch's base (`c8b2182`, current `main` HEAD). #30 warns that #28/#29 may also bump these. Default if one lands first: rebase and take the next minor above whatever `main` then holds — the increment size is the decision, the absolute number is not. A major bump appearing on `main` in the interim is a rebase, not a redesign.
- **`docs/superpowers/` mentions of 2.1.218 stay as they are.** They are dated records of what was believed and measured at the time; editing them would make the history wrong. Both shipped review checks skip that path anyway.
- **The 2.1.220 measurement is taken from #30 and from this run's own dispatch**, not re-derived: the agent that dispatched this design is itself a spawned subagent and holds `Agent`. Recorded as dated evidence in the ADR precisely because it is a measurement of one version and not a standing fact.
- **`SKILL.md:8` and the Pipeline preamble (`:201` / `:195`) need no edit.** Line 8 already says *"work on any Claude Code version, with no nested subagent spawning"* — version-independent and true. The preamble says *"All fan-out work … the orchestrator runs itself, in-context … Only leaf subagents are ever spawned; no subagent spawns a subagent"* — operative, correct, and carrying no version claim; C counts both among the six sites that already carry the prohibition, which is why the bullet keeps only the modality. Checked rather than assumed, because #30 names them as related sites.
- **`plugins/*/skills/adversarial-review/SKILL.md` is read-only here.** The ADR quotes its Review-integrity clause; the file is not touched. A concurrent change owns it.
- **The spawn-topology vocabulary is missing from `CONTEXT.md`.** `orchestrator`, `leaf`, `spawner`, and `topology` appear there zero times; `fan-out` appears once, only inside the *Provenance* entry. That is why this design's review had to spend a resolver disproving a `topology` collision the glossary could not settle. `CONTEXT.md` is out of scope here and the gap is cluster-shaped, not one entry — filed as **#34**, to be decided as its own change.

## Spec self-review

- **Placeholders:** none. Every path, line number, version, and replacement string is literal; the two `SKILL.md` blocks and the ADR block are complete and applicable verbatim.
- **Consistency:** the bullet keeps `leaf`, `fan-out`, `orchestrator`, `spawner` in the senses the pipeline `SKILL.md` already uses; of those four only `fan-out` is in `CONTEXT.md` (the *Provenance* entry), in the same sense. The ADR uses `provenance`, `seed`, `resolver`, and `tier` per `CONTEXT.md`. `topology` is not a glossary term, and it is not a collision either: the protocol exempts "a word the artifact uses in the sense the repo already has", and the repo's only shipped use of the word is the very bullet being replaced, in exactly this sense — a sense both replacement blocks keep verbatim. No ADR uses the word at all; ADR-0001 calls its own subject an *axis*. No `_Avoid_` synonym (`finder`, `first-pass reviewer`, `group agent`, `judge`, `arbiter`, `boundary`) is used as a name in either shipped block or the ADR.
- **Scope:** four files touched — two `SKILL.md`s, two `plugin.json`s — plus one new ADR. No forbidden file appears in the change list. `CONTEXT.md`, `scripts/`, `CLAUDE.md`, and both `adversarial-review/SKILL.md` copies are untouched.
- **Ambiguity:** the one genuine fork (delete the normative clause vs. re-anchor it) is decided in C with the reasoning shown, not defaulted. The one open variable (a colliding version bump from #28/#29) has a defensible default recorded above.
- **ADR conflict check** (`docs/agents/domain.md`): nothing here contradicts ADR-0001 or ADR-0002. ADR-0003 sits on a different axis from ADR-0001 — spawn shape, not source-file duplication — so the two do not meet; it cites ADR-0002 by name on what the provenance line proves, in the sense ADR-0002 establishes.

---

## Verification

Run from the repo root. Steps 1–3 are the `CLAUDE.md` hand-mirrored-pair procedure (residue grep + a per-change design-conformance check); 5–6 are the two repo checks.

1. **Residue — the removed phrases are gone from shipped text.** Expect **no output** and `exit=1` from each:

   ```sh
   grep -rn -F '2.1.218' plugins/; echo "exit=$?"
   grep -rn -F '2.1.217' plugins/; echo "exit=$?"
   grep -rn -F 'does not grant spawned subagents' plugins/; echo "exit=$?"
   grep -rn -F 'is why 1.2.0 flattened' plugins/; echo "exit=$?"
   grep -rn -E '2\.1\.2' plugins/; echo "exit=$?"
   ```

   Scoped to `plugins/` deliberately: this design and ADR-0003 both quote these strings, and both are correct places for them to appear.

2. **The normative clause survives in both copies.** Expect exactly **2** — one per pipeline `SKILL.md`, and no third copy anywhere under `plugins/`:

   ```sh
   grep -rc -F 'This is required, not a preference:' plugins/ | grep -v ':0$'
   ```

3. **Design conformance — the replacement bullets and the ADR landed verbatim, in the right place.** `check-sync.py` never reads the pipeline pair, so this is the only thing standing between the design and a paraphrase, and the only check anchored *outside* the pair. It re-reads all three payload blocks from this design file on disk — never retyped — and asserts each appears byte-for-byte in its target, that each bullet sits directly under `## Environment Assumptions`, that neither file changed length, and that the two bullets are exact substitution images of one another. Pure ASCII on purpose: a mistyped copy fails loudly rather than passing, and the non-ASCII characters live only in the blocks it reads. **Every failure is a `MISMATCH:` line, never a traceback** — an unreadable target is reported like any other mismatch, so a run before the ADR exists lists everything still outstanding instead of aborting on the first missing file. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path

DESIGN = "docs/superpowers/specs/2026-08-02-gh-30-flat-topology-design.md"
ANCHOR = "## Environment Assumptions"
TARGETS = [
    ("plugins/dev-flow/skills/dev-flow/SKILL.md", 277),
    ("plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md", 271),
]
ADR = "docs/adr/0003-flat-topology-for-the-dev-flow-pipelines.md"
GONE = [
    "does not grant spawned subagents",
    "is why 1.2.0 flattened",
    "2.1.218",
    "2.1.217",
]
FENCE = chr(96) * 3

bad = []

def read(path):
    try:
        return Path(path).read_text(encoding="utf-8").split("\n")
    except (OSError, UnicodeDecodeError) as e:
        bad.append("%s: cannot read (%s)" % (path, e.__class__.__name__))
        return None

def report():
    for why in bad:
        print("MISMATCH:", why)
    print("design-conformance:", "FAIL" if bad else "OK")
    sys.exit(1 if bad else 0)

design = read(DESIGN)
if design is None:
    report()

blocks, cur, mode = [], None, None
for line in design:
    s = line.strip()
    if mode is None:
        if s.startswith(FENCE):
            mode, cur = s[3:], []
    elif s == FENCE:
        if mode == "":
            blocks.append(cur)
        mode, cur = None, None
    else:
        cur.append(line)

shape = [len(b) for b in blocks]
if len(blocks) != 3:
    bad.append("design has %d plain-fenced blocks, want 3" % len(blocks))
elif shape[:2] != [1, 1]:
    bad.append("design's two bullet blocks are %s lines, want 1 each" % shape[:2])
if bad:
    report()

for (path, want_len), block in zip(TARGETS, blocks[:2]):
    want = block[0]
    lines = read(path)
    if lines is None:
        continue
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != want_len:
        bad.append("%s is %d lines, want %d" % (path, len(lines), want_len))
    at = [i for i, l in enumerate(lines) if l == want]
    if len(at) != 1:
        bad.append("%s: bullet found %d times, want exactly 1" % (path, len(at)))
    elif not (at[0] >= 2 and lines[at[0] - 1] == "" and lines[at[0] - 2] == ANCHOR):
        bad.append("%s: bullet does not sit first under %r" % (path, ANCHOR))
    body = "\n".join(lines)
    for g in GONE:
        if g in body:
            bad.append("%s: removed phrase survives: %r" % (path, g))

if blocks[1][0].replace("dev-flow-worktree", "dev-flow") != blocks[0][0]:
    bad.append("the two bullets are not substitution images of each other")

adr_lines = read(ADR)
if adr_lines is not None:
    while adr_lines and adr_lines[-1] == "":
        adr_lines.pop()
    if adr_lines != blocks[2]:
        bad.append("%s does not match the design's ADR block exactly" % ADR)

report()
PY
echo "exit=$?"
```

   Expect exactly `design-conformance: OK` and `exit=0`. The `!= 3` guard fires if this document's plain-fenced blocks are ever added to or reordered — every other fence here carries an info string (`text`, `sh`), so adding a verification step never disturbs the index. **Keep it that way.** That guard and the one-line-block check stop the run rather than continuing: with the payload blocks malformed there is nothing left to conform to, and the design is what needs fixing first.

4. **Versions moved, and by one minor.** Expect `dev-flow` at `2.7.0` and `dev-flow-worktree` at `1.9.0`, each on a line naming its own file:

   ```sh
   git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
   ```

   `git grep`, not bare `grep`: the assertion is *which plugin is at which version*, and only `git grep`'s path-labelled, path-sorted output makes that deterministic.

5. **`python3 scripts/check-sync.py`** — passes. Expect the three lines unchanged from baseline, since no file it reads is touched:

   ```text
   check-sync: manifest descriptions ... OK (8 plugins)
   check-sync: mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)
   check-sync: all checks passed
   ```

   Note what this does **not** cover: the pipeline `SKILL.md` pair is not enrolled, so a one-sided edit passes it silently. Step 3 is the check that would catch that.

6. **`claude plugin validate .`** — passes. Expect exactly **8** `No author information provided` warnings and **exit 0**. Those warnings are the expected steady state, not a failure.

7. **Forbidden files untouched.** Expect no output:

   ```sh
   git diff --name-only main -- CLAUDE.md CONTEXT.md scripts/ 'plugins/*/skills/adversarial-review/'
   ```

## PR

```text
Closes #30
```
