---
dev-flow:
  slug: gh-10-opus-resolver
  stops: [pre-merge]
  docs: commit
---

# gh-10: swap the `fable` resolver tier for `opus`

## Goal

Make `opus` the unconditional group-resolver tier in `adversarial-review`, replacing the current `fable`-with-`opus`-fallback rule, because Opus 5 closed enough of the capability gap that Fable's premium no longer earns its cost for this workload. Seeds stay on `sonnet`; executors, fixers, and the orchestrator stay on the main session model. Because the current rule justifies itself with an `adversary ≠ author` framing that an unconditional `opus` resolver tier collapses, the change is not a token swap: every clause that claims or verifies "model diversity" — in both `adversarial-review/SKILL.md` copies and both pipeline `SKILL.md` copies — must be restated to assert only what remains true. The end state is a review protocol with two fixed tiers (`sonnet` seeds, `opus` resolvers), no ambient-state-dependent model selection anywhere, and a provenance check whose prose describes exactly the property it mechanically verifies.

## Scope check

This is one coherent change, not a decomposable set. The five prose files and two manifests all move together: editing the Model section without editing the provenance enum leaves the review able to report a tier the Model section forbids; editing either `adversarial-review` copy without the other fails `scripts/check-sync.py`; bumping neither version means neither edit is ever picked up by a re-sync; and the `CLAUDE.md` sentence (change 7) records the backstop this change's own hand-mirrored pair depends on, so it lands with the pair or not at all. There is no independent subsystem to split out, and no halt is warranted.

## The open question, resolved

### The question

The current design's stated rationale for the resolver tier is that resolvers must run on a model family **different from the artifact's author**. Under dev-flow, the author is a produce-subagent on the main session model, which is normally Opus. Moving resolvers to `opus` therefore makes author and adversary the same family, and the orchestrator's provenance check — described as confirming "the review was genuinely model-diverse" — would be asserting something that no longer holds.

### Decision: Option 1 — accept the collapse, and restate the guarantee precisely

Resolvers run on **`opus`, unconditionally, with no session-model-dependent fallback**. Seeds stay on `sonnet`. The `fable` alias is removed from the protocol entirely, including from the provenance `<tier>` enum. Every clause claiming family-level diversity is rewritten to claim what the protocol actually delivers and what the provenance check actually proves.

This is the issue's Option 1, adopted with one sharpening of how Option 1 states the residual guarantee. Option 1's sketch says the check now guarantees "tier separation, not family separation." That is still not quite what the check does, and getting it exactly right is the point of the rewrite:

- **What the provenance check has always verified is tier *conformance*, not diversity of any kind.** The check compares the reported per-tier aliases against the tiers the Model section specifies. It has never had any knowledge of which model authored the artifact, so it could never have verified `adversary ≠ author` — not before this change and not after. The "genuinely model-diverse" wording was already an overstatement of a check that proves something narrower.
- **What that narrower thing is, is still worth having.** A conforming provenance line is mechanical evidence that the review really fanned out into separate reviewer subagents on the declared tiers, instead of collapsing into a single inline pass — which is precisely the failure mode "Review integrity (never inline)" exists to prevent. That is the guarantee, and the rewritten prose should name it.

### Why the `adversary ≠ author` property survives the collapse in useful part

The property decomposes into two independent components:

1. **Contextual independence** — the reviewer runs in a fresh context window, holds no memory of authoring the artifact, does not know the artifact is its own output, and is prompted to attack rather than defend it. This eliminates self-consistency bias and the anchoring that comes from having produced the reasoning trace. It is entirely unaffected by model family.
2. **Prior independence** — the reviewer's training-induced blind spots are uncorrelated with the author's. This is the component a same-family adversary loses.

Component 1 carries most of what this protocol is built to surface — with one honest qualification. In design and plan modes the seed checklists are prose integrity, internal contradiction, unstated assumption, missing success criteria, task ordering, and plan-vs-design drift; in diff mode they are the `/simplify` angles and the pinned code-reviewer template. These are checklist-driven findings a fresh, hostile reader is positioned to catch, and to the extent uncorrelated training priors help, they help at the *noticing* step — which stays on `sonnet`, cross-family from an Opus author, under this change. Component 2's distinct value concentrates in the resolvers' subtle judgment calls, and losing it there is a real loss, not a rounding error — including in the Stage-4 diff review, where the code's authors (Execute-stage subagents on the main session model) and the resolvers become the same family on a default Opus session. This design does not demonstrate that the loss is small; it accepts it on the issue's stated premise — the user's judgment that Opus 5 is now close enough on exactly these calls that Fable's premium no longer buys its cost back. That premise is a cost/capability call only the user can make; it is the reason the issue exists, and it enters this design as a requirement, not a conclusion the design derives.

Two further observations support accepting the loss rather than engineering around it:

- **The old rule already treated family separation as negotiable.** The existing fallback swaps one premium family for the other purely to keep the families distinct. A property whose implementation is "use whichever of these two is not the session model" was never a hard invariant — it was a preference expressed as a two-way swap.
- **Some cross-family signal survives for free.** Seeds run on `sonnet`, a different family from an Opus author, and seeds are what determine *what gets noticed*. This is a genuine residual benefit. It is deliberately recorded as a happy consequence of the seed tier's cost choice, **not** promoted to an enforced guarantee (see the rejection of Option 3).

### Cost vs. signal

Under the chosen option, every run's resolvers move off the premium tier — the full cost reduction the issue asks for, with no conditional path that quietly restores the old spend. The signal given up is component 2 on the resolver tier only. Seeds are unchanged, contextual independence is unchanged, the adversarial framing is unchanged, and the inline-review halt is unchanged.

### Rejected alternatives

**Option 2 — invert the fallback (default `opus`, fall back to `fable` when the session model is Opus-family).** Rejected on two counts. First, it defeats the motivation: the session model is normally Opus, so the fallback fires on most runs and the premium is still paid — mostly a no-op on cost. Second, and more damaging long-term, it keeps the resolver tier a function of ambient session state. The orchestrator's provenance check would then have to know which model the session is running on before it could decide whether `resolvers: 3× fable` is conforming or a violation. That converts a fixed comparison into a stateful one, in a check whose entire value is being cheap and mechanical. Keeping a conditional to preserve a property the check cannot verify anyway is the worst of both.

**Option 3 — move the diversity guarantee onto the seeds.** Rejected. It reads as attractive because `sonnet` seeds against an Opus author *are* cross-family today — but making that a *guarantee* rather than an observation requires the seed tier to become conditional on the session model (a Sonnet session would force seeds off `sonnet`), reintroducing exactly the ambient-state dependency that sinks Option 2. It also mislocates the property: seeds are findings-only and make no judgment calls, so cross-family value there affects what gets noticed, not what gets decided — a weaker place to hang a stated guarantee than where the old rule put it. And it does not fix the underlying honesty problem, because the provenance check still has no idea what model authored the artifact; renaming the enforced property from "resolver-tier diversity" to "seed-tier diversity" would produce a second claim the check cannot substantiate. The true part of Option 3 is kept as rationale in the seed paragraph; only the enforcement is dropped.

**Option 4 (considered, rejected) — drop the provenance line entirely, since it cannot prove diversity.** Rejected: the line is still the only mechanical evidence that "Review integrity (never inline)" was honored. Removing it would delete a working check because its *description* was wrong. Fix the description.

**Option 5 (considered, rejected) — record the author's model family and enforce `adversary ≠ author` against it.** The machinery is real: produce-subagents run on a main session model the orchestrator already knows, the design doc's `dev-flow` front-matter exists precisely to carry durable cross-stage state, and `adversarial-review` contractually preserves front-matter across rewrites — so Stage 1 could stamp an author family, and the family-match check could compare resolver self-reports against the recorded family instead of a fixed tier. Rejected because the recorded field cannot buy the property back at the price the issue sets. (1) On a default Opus session the recorded family is Opus and the resolver tier is `opus`, so an enforcing check fails on essentially every run; its only exits are a family-conditional premium fallback — Option 2 with its condition read from front-matter instead of ambient state, restoring the very spend the issue removes — or resolvers below `opus`, a deeper capability cut than the issue chose. A non-enforcing variant that merely records the comparison changes no behavior and verifies nothing. (2) The "author" is not one family: design-file entry's author is the user, who has none; every reviewed artifact is then rewritten by fixer agents on the main session model; and a resumed run may span sessions on different models — one stamped field misdescribes all of that. (3) Diff mode has no front-matter — the artifact is the branch itself — so a recording site (per-commit trailers, a sidecar file) would have to be invented for a check that (1) already shows cannot affordably enforce anything. (4) Standalone invocations have no produce-subagent and no stamp, forcing an absent-means-skip branch into the check — the conditional, state-dependent comparison Options 2 and 3 were rejected for. What is true in Option 5 — that the author's family is knowable and recordable — does not change what is affordable: the property fails not for want of measurement, but because the user has chosen to stop paying for the only tier that would make it true.

### Should `fable` stay in the provenance `<tier>` enum?

No — remove it. After this change exactly two tiers may be spawned, so a `fable` entry in the enum is unreachable by construction. An unreachable-but-legal alias is actively harmful here: it makes `resolvers: 3× fable` parse as a well-formed provenance line, which is precisely the "the review ran on the wrong model" case the check exists to catch. Narrowing the enum to `{sonnet, opus}` makes the set of legal answers equal to the set of reachable answers, so an off-tier report is rejected by the enum itself rather than needing a separate rule. Correct-by-default.

The **family-match clause stays**, minus its fallback sub-clause. Family matching was never about the fallback: a reviewer's self-report names a product ("Claude Opus 5"), not a harness alias, and dated model ids drift, so matching by family is what makes the check robust at all. What drops is the "honoring the resolver opus-fallback" qualifier, which existed only because the requested resolver tier was conditional. The clause's example must also move off `fable` — an example naming a tier the enum no longer contains would be a trap for the next reader.

One structural fix rides along in the rewrites above. This is the second tier change to force the same four-spot lockstep edit inside each `adversarial-review/SKILL.md` (lines 18, 59, 69, 73/75 — introducing the fallback did it once, removing it does it again), and `check-sync.py` only enforces agreement *between* the two copies, never *within* one file. So the replacement text stops restating the roster wherever the restatement is not load-bearing: the seed-passes first mention, the resolution-procedure step, and the family-match clause now point at Model instead of naming aliases. What still names tiers is exactly what must: the Model section (the owner) and this enum (deliberately explicit, so an off-tier report is ill-formed by construction — the point of this section), plus illustrative examples, which are leftover-text-detectable by the same residue-grep idiom the Verification section uses for `fable`. The next tier change edits Model, the enum, and two examples — no normative restatements left to silently miss.

## Exact change list

Seven files. Every wording below is the literal replacement text.

### 1 & 2. `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`

These two are a declared `check-sync.py` mirror pair. **Every edit below lands identically in both files**, with the sole difference being the `dev-flow` / `dev-flow-worktree` variant tokens already present in line 69, which the mirror check canonicalizes away. No line is added or removed in either file; all six edits are in-place and none spans a line break, so both files stay at 81 lines. Five replace a whole line; the sixth (line 24) replaces a phrase inside one.

#### Line 18 — Review integrity, family-match clause

Replace the whole line with:

```
**Review integrity (never inline).** The seed and resolver passes MUST run as separate subagents on their specified models (per Model, below). If they cannot be spawned — no `Agent` tool, or a required model unavailable — halt and report; **never** produce a single-model inline review as a silent substitute. To make the model axis verifiable, every reviewer prompt (seed and resolver) requires the reviewer to state, as the first line of its report, the model its own system prompt names. The review matches each self-report to the tier requested for it — a **family match** (e.g. an "Opus 5" self-report satisfies the `opus` tier) rather than a hardcoded dated id, because a self-report names a product and dated ids drift — and canonicalizes it to that tier's alias. A missing or mismatched first line is treated exactly like a failed spawn: halt.
```

Changes: the example moves from `"Fable 5"` / `` `fable` `` to `"Opus 5"` / `` `opus` ``; the "honoring the resolver opus-fallback" qualifier is replaced with the durable reason family matching is used at all; and the canonicalization no longer restates the alias roster — it maps each self-report to the requested tier's alias, leaving the tier set stated normatively only by Model and the step-6 enum (see the enum section's closing paragraph).

#### Line 24 — Seed passes, the seed-tier first mention

A phrase-level edit, not a whole-line replacement. Replace `on the seed-reviewer model (`sonnet` — see Model, below)` with `on the seed-reviewer model (see Model, below)`. Nothing else on the line changes.

This is the same de-restatement applied to line 59 below, at the seed tier. It is included because without it the invariant this section claims — that no normative tier restatement survives outside Model and the step-6 enum — would be false: line 24 is exactly such a restatement, and leaving it would mean the next seed-tier change has one more place to remember, in a document that tells the reader there are none. The two tiers' first mentions also end up in the same shape, so the next editor cannot copy the wrong one.

Deliberately **not** given as a fenced block: the design-conformance check in the plan's verification enumerates this document's plain-fenced blocks positionally, and this edit was added during the PR review, after that check was authored and run. Documenting it as a phrase edit (as line 8's is) leaves that check valid and re-runnable. The edit is small enough to verify by grep — see Verification step 6.

#### Line 59 — Resolution procedure, step 2

Replace the whole line with:

```
2. Group similar issues together. For each group, spawn one agent, on the resolver model (see Model).
```

#### Line 69 — Report-back, step 6

Replace the whole line with (this is the **`dev-flow`** copy; in the `dev-flow-worktree` copy, both occurrences of `dev-flow` in the final sentence read `dev-flow-worktree`, exactly as they do today):

```
6. Report back: the commit(s) made, a summary of applied vs. skipped fixes, the post-fix suite result (diff mode), every new issue filed, and a **provenance** line naming the reviewers actually spawned per tier with their canonicalized tier aliases (from Review integrity's family match), in the form `seeds: N× <tier>; resolvers: M× <tier>` with `<tier>` ∈ {`sonnet`, `opus`} (e.g. `seeds: 2× sonnet; resolvers: 3× opus`; a review that surfaces no findings spawns no resolvers and reports `resolvers: 0`, tierless). Provenance is the evidence the invoking caller (dev-flow's orchestrator, when called by dev-flow) checks directly to confirm the review really fanned out to separate reviewer subagents on the tiers this section specifies — never a single inline pass.
```

Changes: enum drops `fable`; the example resolver tier becomes `opus`; the closing claim changes from "genuinely model-diverse" to the fan-out/tier-conformance property the check actually establishes.

#### Line 73 — Model, group-resolution agents

Replace the whole line with:

```
**Group-resolution agents** — the tier that determines the best long-term design and adversarially self-checks — run on `opus` (a harness alias, never a dated model id), unconditionally, with no session-model-dependent fallback. Their independence from the artifact's author is **contextual, not cross-family**: a fresh context window with no memory of authoring, an explicitly adversarial prompt, and a spawn that provenance verifies out of band. A session-model-conditional tier would buy back family separation only by making the resolver tier depend on ambient state, which the provenance check could no longer compare against a fixed expectation.
```

#### Line 75 — Model, seed reviewers

Replace the whole line with:

```
**Seed reviewers** — the findings-only quality and correctness passes — run on `sonnet`: cheaper than `opus`, and in the common case a different family from the author, which is a bonus on what gets *noticed* rather than a guarantee this protocol enforces. They only surface findings; the resolvers do the judgment, so the resolver tier's cost isn't warranted here.
```

Line 77 (`**Executors, fixers, and the orchestrator** run on the main session model.`) is unchanged.

### 3 & 4. `plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`

These two are **not** a mechanically checked mirror pair — `check-sync.py` will not catch a one-sided edit. Both must be edited by hand, in parallel. Line numbers below are `dev-flow` first, `dev-flow-worktree` second.

#### Line 8 (both files) — intro paragraph, "the model-diverse review"

Within the existing sentence, replace the phrase `the model-diverse review` with `the multi-agent review`. Nothing else on the line changes. The point that sentence is making is that the fan-out survives the flat-topology constraint, which is still exactly true; only the "diverse" adjective is now a claim the protocol no longer makes.

#### Line 46 (`dev-flow`) / line 45 (`dev-flow-worktree`) — Model Policy

The current text says reviewer-model selection is "stated once, in its Model section" and then restates it inline ("on a capable model different from the artifact's author") — a self-contradiction today, and the restated half becomes false with this change. Replace the whole line with (this is the **`dev-flow`** copy; the `dev-flow-worktree` copy uses `dev-flow-worktree:adversarial-review`, exactly as it does today):

```
The orchestrator spawns produce-subagents and executors on the main session model, and does its own bookkeeping (checkbox commits, front-matter) inline. Reviewer-model selection — which tier the orchestrator spawns each of the review's seed/resolver leaves on — is owned by `dev-flow:adversarial-review` and stated once, in its Model section; that rule travels with the review skill wherever it is invoked, and is deliberately not restated here.
```

This puts the tier rule in exactly one place, so the next tier change touches one file pair instead of two.

#### Line 273 (`dev-flow`) / line 267 (`dev-flow-worktree`) — Cross-Cutting Concerns, "Review provenance is checked, not assumed"

Only the bullet's final sentence changes. The mechanical description earlier in the bullet ("seeds must be the seed tier, resolvers the resolver tier") is already tier-relative and stays verbatim. Replace the whole line with (this is the **`dev-flow`** copy; the `dev-flow-worktree` copy uses `dev-flow-worktree:adversarial-review`, exactly as it does today):

```
- **Review provenance is checked, not assumed.** The orchestrator runs each review (Design, Plan, PR — not Execute) in-context, then reads the review's returned provenance line (`seeds: N× <tier>; resolvers: M× <tier>`) directly and halts if it is missing or its tiers violate `dev-flow:adversarial-review`'s Model section (seeds must be the seed tier, resolvers the resolver tier; a `resolvers: 0` line from a no-findings review passes the resolver check vacuously). The tiers are canonicalized by the review's family match, so this is a direct comparison — a cheap self-check that the review actually fanned out to separate reviewer subagents on the specified tiers, rather than folding into a single inline pass.
```

### 5 & 6. Version bumps

- `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.2.0"` → `"version": "2.3.0"`.
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.4.0"` → `"version": "1.5.0"`.

Required, not cosmetic: the install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an edit at an unchanged version is never picked up on re-sync.

### 7. `CLAUDE.md` — record the residue-grep backstop as standing policy

Append one sentence to the "Changing a plugin" bullet that currently ends "…mirror those by hand.":

```
For any hand-mirrored edit, put a residue grep in the change's verification — grep for the exact phrases the edit removes, expecting no hits — since a one-sided miss leaves the old text behind and nothing else catches it.
```

This earns its place because the next person doing a hand-mirrored edit reads the auto-loaded `CLAUDE.md`, not this design doc. It puts the backstop at the shared boundary so every future hand-mirrored edit inherits the pattern, instead of each change reinventing it — which is exactly what this change had to do (see §Sync constraint).

### Blast radius — verified complete

A repo-wide search outside `docs/` for `fable`, `opus`, `sonnet`, `resolver`, `model-diverse`, and `diversity` confirms the change list is complete, with one caveat a rerun of that search must expect: not every hit is an edit target. `fable`, `opus`, and `model-diverse` occur only on lines the change list already replaces, and `diversity` occurs nowhere. The other two terms have benign residual hits that must **not** be edited: `sonnet` appears at `plugins/better-code-review/skills/better-code-review/SKILL.md:13`, an unrelated plugin's own reviewer fan-out (line 24 of both `adversarial-review/SKILL.md` copies was a third benign hit when this section was first written; the PR review then de-restated it — see the Line 24 entry above — so it is now an edit target, not a residual); `resolver` appears as a plain tier name on unchanged lines 20 and 63 of both `adversarial-review` copies, and in an unrelated sense entirely — the branch/`<username>` resolver — at `plugins/dev-flow/skills/dev-flow/SKILL.md` lines 78 and 268 and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` lines 76 and 262. (This is also why Verification step 3 pins the mechanical post-change check to `fable` alone: it is the one term with no homonym, so empty output is meaningful.) Specifically confirmed clean and requiring **no** tier edit: both `plugins/dev-flow*/README.md` (no model or tier references at all), `.claude-plugin/marketplace.json`, `scripts/check-sync.py`, `.github/workflows/check-sync.yml`, and `docs/agents/*.md`. `CLAUDE.md` likewise needs no tier edit, but this change does add one sentence to its hand-mirroring bullet (change 7) so the residue-grep backstop becomes standing policy rather than a one-off. The `.superpowers/` SDD scratch tree is out of scope whatever it happens to contain: it is git-ignored (`.superpowers/sdd/.gitignore` contains `*`), so `git grep` never sees it, and it holds per-run in-session artifacts rather than repo content — leave it alone.

## Sync constraint

`scripts/check-sync.py` runs on every PR and must still pass.

**Check B (mirror pair `adversarial-review`)** requires the two `adversarial-review/SKILL.md` files to be line-for-line identical after substituting `dev-flow-worktree` → `dev-flow` on both sides, except for the one declared exception (the `working-dir` bullet at line 12). This imposes three requirements on the edit:

1. **All six edits must land in both files.** A one-sided edit produces an undeclared-divergence failure naming the line.
2. **No line may be added or removed in either file.** All six edits are in-place and confined to one line each, so both files remain at 81 lines. A line-count mismatch is a distinct, harder-to-read failure mode (`LINE_COUNT_FIX`), and the pair's schema can only express same-index one-line-for-one-line divergences — so a new one-sided line could not be declared as an exception even if someone wanted to.
3. **The variant tokens on line 69 must stay in place.** The replacement text for line 69 keeps `dev-flow's orchestrator, when called by dev-flow` in the `dev-flow` copy and `dev-flow-worktree's orchestrator, when called by dev-flow-worktree` in the worktree copy; those canonicalize to the same string, so the line still compares equal.

**No new exception is needed, and none becomes stale.** The single declared exception covers line 12, which this change does not touch — so it still fires, and the "stale exception" check stays satisfied.

**Check A (manifest descriptions)** compares `name`, `source`, and `description` between each `plugins/<name>/.claude-plugin/plugin.json` and its `.claude-plugin/marketplace.json` entry. It does **not** read `version`. This change edits only `version` in both manifests and no `description` anywhere, so Check A is unaffected and `.claude-plugin/marketplace.json` is not edited. (The CLAUDE.md rule that `description` must stay in sync across both manifests remains in force; it simply has nothing to do here.)

The `dev-flow` / `dev-flow-worktree` pipeline `SKILL.md` pair is **not** enrolled in `MIRROR_PAIRS`, and cannot be: the two files differ in length (277 vs 271 lines) and Check B's schema only expresses line-for-line parallelism. Hand-mirroring this pair is settled policy (issue #8, `CLAUDE.md`). Its three edits are therefore mirrored by hand, and a one-sided miss passes every mechanical check in CI — `check-sync.py` never reads this pair, and `claude plugin validate .` reads manifests, not skill prose. The `fable` grep (Verification step 3) is no backstop either: none of the three pipeline edits contains that word. The real backstop is Verification step 4 — each pipeline edit *removes* a distinctive phrase (`model-diverse`, `diverse reviewers`, `different from the artifact`) that afterwards appears nowhere in tracked files outside the immutable history, so a one-sided miss leaves the old phrase on the unedited side and the grep fails loudly. What no grep can verify is that the *new* prose landed correctly in both copies; that residual risk is accepted by the hand-mirroring policy and is covered by reading the two copies side by side.

## Out of scope

- **The `adversarial-review/SKILL.md` duplication itself.** Consolidating the two copies is issue #8's job. This change mirrors the edit by hand into both copies, as the current structure requires, and does not touch `scripts/check-sync.py` or `MIRROR_PAIRS`.
- **Historical records under `docs/superpowers/specs/` and `docs/superpowers/plans/`.** These record what was decided at the time and are immutable. They contain `fable` references that are correct as history, and none may be edited, rewritten, or "brought up to date." The verification greps are scoped to exclude them for exactly this reason.
- **Any other model-tier change.** Seeds stay `sonnet`; executors, fixers, and the orchestrator stay on the main session model. No new tiers, no per-mode tier selection, no configurability.
- **The provenance mechanism itself.** The line's format, the first-line self-report requirement, the halt-on-mismatch rule, and the orchestrator's comparison all keep their current behavior. Only the enum's contents and the sentences describing what the check proves change. Extending the mechanism to record the artifact's author family was considered and rejected as Option 5 under Rejected alternatives — this bullet scopes the mechanism out as *unchanged*, not as *unexamined*.
- **`.superpowers/sdd/` scratch files**, which are git-ignored.
- **The two `README.md` files**, which contain no model or tier references.

## Verification

Run every step from the repo root; all must pass before the change is considered done.

1. **Mirror and manifest sync:**

   ```sh
   python3 scripts/check-sync.py
   ```

   Expect `check-sync: all checks passed`, with the mirror pair reporting `81 lines, 1 declared exception` — the same line count as before the change, confirming requirement 2 above.

2. **Marketplace validation:**

   ```sh
   claude plugin validate .
   ```

   Expect success. **8 missing-author warnings are expected** and are not a failure.

3. **No stale `fable` resolver references survive outside `docs/`:**

   ```sh
   git grep -ni 'fable' -- ':!docs/superpowers'
   ```

   Expect **no output** (exit 1). `git grep` searches tracked files only, so the git-ignored `.superpowers/` scratch is excluded automatically; the pathspec excludes the immutable historical specs and plans. Note: do not write this as `-E '\bfable\b'` — `\b` is not honored by git's regex engine here and the command silently matches nothing, which would look like a pass no matter what the tree contains.

4. **No one-sided pipeline-pair edit survives:**

   ```sh
   git grep -niE 'model-diverse|diverse reviewers|different from the artifact' -- ':!docs/superpowers'
   ```

   Expect **no output** (exit 1). Each of the three hand-mirrored pipeline edits removes one of these phrases, and after the change they appear nowhere in tracked files outside the immutable history (the `adversarial-review` lines that also lose them are already guarded by step 1's mirror check). Any hit is an unedited side of the pipeline pair — this is the backstop `check-sync.py` cannot provide for that pair. Like step 3, it detects leftover old text, not a botched replacement; the new prose itself is verified by reading the two copies side by side.

5. **Spot-check the two version strings** — `grep -n '"version"' plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json` should show `2.3.0` and `1.5.0`.

6. **The line-24 de-restatement landed in both copies:**

   ```sh
   git grep -nF 'seed-reviewer model (`sonnet`' -- ':!docs/superpowers'
   ```

   Expect **no output** (exit 1). This is the residue check for the Line 24 edit, and it is needed because `check-sync.py` structurally cannot cover that edit: the mirror check compares the two copies to *each other*, so a miss on **both** sides leaves them identical and passes clean. Only a residue grep sees it. `-F` is deliberate — the pattern contains a backtick and a parenthesis, and a fixed-string match avoids any regex interpretation.

## Assumptions recorded

- **`opus` is a valid harness alias.** The Model section forbids dated model ids and requires aliases; `opus` already appears as an alias in the clause being removed, so it is known-good in this position. No new alias is introduced.
- **Minor version bumps.** `2.3.0` and `1.5.0` per the issue. Behavior changes but no interface does — the skill's invocation signature, provenance line format, and contract are unchanged — so minor, not major.
- **Replacement phrase for "model-diverse" in the intro line.** `multi-agent review` is chosen as the defensible default: it preserves the sentence's actual point (the fan-out survives flat topology) without asserting diversity.
- **Fixing the Model Policy restatement is in scope.** The clause "on a capable model different from the artifact's author" is the exact text this change falsifies, so it must be edited regardless; replacing it with a non-restating pointer rather than an updated restatement is the minimal correct fix and removes a pre-existing contradiction with the same sentence's own "stated once" claim.
- **The `fable` alias is removed from the protocol, not merely deprecated.** No transitional period, no "accepted but discouraged" enum entry — the alias becomes unreachable, so it leaves.
