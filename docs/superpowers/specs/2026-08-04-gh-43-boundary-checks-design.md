---
dev-flow:
  slug: gh-43-boundary-checks
  stops: [pre-merge]
  docs: commit
---

# gh-43: a home for merge-time checks, and a merge gate that re-runs them

**Ruling: SHIPS**, as a small, coordinated set of prose edits to both pipeline `SKILL.md` twins that introduce one new idea — a **merge-time check** — and give it exactly one home to be authored (the plan) and exactly one place to be discharged (the merge gate). This closes both of issue #43's gaps with one construct, not two. No new box syntax, no general "re-run every success criterion" engine.

The subject of this design is dev-flow's own `SKILL.md` prose. There is no code or test surface; the correctness surface is the edited Markdown, so every success criterion below is a runnable grep or structural assertion, never a judgement call.

## The two gaps, grounded in current text

Both gaps live in `plugins/dev-flow/skills/dev-flow/SKILL.md` and its hand-mirrored twin `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`. The issue's line numbers are stale; the anchors below are quoted from the current files (dev-flow numbering; the twin is ~6 lines earlier and names `dev-flow-worktree`).

### Gap 1 — a `- [ ]` cannot express a step that runs after Execute

Three current sentences, together, force every checkbox in a plan to be completable inside Stage 3 (Execute):

- **Execution-complete signal** (dev-flow `:165`): *"Execution is complete if and only if the plan at branch tip has zero unchecked task boxes — lines matching `^[[:space:]]*[-*+] \[ \]` …"*
- **Stage 3 exit condition** (`:229`): *"Exit condition supersedes SDD's terminal: last task complete, per-task reviews clean, full suite green, on the named branch."*
- **Resume table** (`:191`): *"Plan at tip has ≥1 unchecked task box … | Execute — resume at first unchecked task"* — a row evaluated **above** the marker rows, first match wins.

A criterion that can only run *later* — after the PR exists, after the last `origin/main` integration, immediately before the `pre-merge` halt — therefore has no legal home as a checkbox:

- **Left unticked**, it makes Stage 3's exit unsatisfiable on the first pass, and on resume the Execute row (`:191`) fires above the marker rows and routes a fully-reviewed, marker-and-CI-ready PR back into Execute — one wasted adversarial-review diff pass and a second halt cycle.
- **Ticked where its step actually runs**, the tick is a commit landing after the marker was posted; under `docs: commit`, Marker validity's strip clause is unsatisfiable, so the branch halts with an **invalid** marker and the resume routes to a full re-review of an already-clean PR — the pipeline's most expensive operation.

The measured instance is #38's plan. Its design criterion 7 required a version re-check "immediately before the pipeline halts at `pre-merge`". Because that step has no checkbox home, the plan carried it as **§ *Run 7b — an orchestrator step at the `pre-merge` halt`** — a named, box-free prose section, handed to the orchestrator by the final task's last checkbox, guarded by a Global Constraint *"No checkbox outside Tasks 1–3."* It works, but it is a per-plan reinvention of missing pipeline vocabulary, and it is strictly weaker than a checkbox: **nothing mechanically detects that the prose step was skipped.** The #38 plan says so itself — *"That the plan can only state this precondition and not enforce it is a gap in the pipeline spec, not in this plan"* — and recommends filing this issue.

### Gap 2 — the merge gate re-verifies only SHA-anchored facts

The merge gate (Stage 5, `:243`–`:255`) is five steps: push + confirm the marker (`:247`), a bounded CI wait against the current head (`:248`), consult `stops` (`:253`), strip (`:254`, a no-op under `docs: commit`), and `gh pr merge --squash` (`:255`). Every one of those re-verifies a fact **anchored to the branch SHA** — the marker certifies "reviewed and suite-green at *this exact SHA*", and `gh pr checks` reports the checks that ran on *this exact SHA*.

A `pre-merge` halt can sit for days — that is what the stop is for (`:36`) — and in that window `origin/main` moves. **The marker stays valid throughout, correctly**: the SHA did not change. What changed is the world. Any criterion whose verdict is a function of *the current `origin/main`* rather than of the branch SHA — the whole class of "strictly greater than / must not collide with what is published" — is verified once, at the halt, and never re-entered. The gate's own re-entrancy invariant (`:245`, *"first run and resume travel the identical path"*) is honest about the five steps and silent about the design's criteria, which are re-entered nowhere.

**The measured instance, and its current CI coverage — stated honestly.** #38 measured a version collision: PR #37 was designed against `2.7.0`/`1.9.0`; PRs #35/#36 merged those exact numbers while it was in flight. Because both sides write the byte-identical `"version"` line, merging `origin/main` into the branch auto-resolves with no conflict, the squash produces no version change, and the change ships at an already-published version the version-keyed install cache never picks up.

Since #43 was filed, **issue #48 shipped** (commit `a800f90`): `.github/workflows/check-version-bump.yml` now runs `python3 scripts/check-version-bump.py origin/main` on every PR, failing any touched plugin whose version is not ahead of `origin/main`'s tip. Verified against the script and workflow on disk. This **does** catch the version instance — but only at the moments GitHub re-runs the check, and that is the crux:

- The workflow triggers `on: pull_request`, which fires on **head** changes (open, synchronize, reopen). It does **not** re-run when the *base branch* advances while the head is unchanged.
- A `pre-merge` pause is exactly a period with **no head change**. `origin/main` moving during it does not re-trigger the workflow.
- dev-flow's merge-gate CI wait (`:248`) runs `gh pr checks <pr> --watch`, which reports the **last completed** check runs — stale-green after a base move. The gate does not notice.
- The one mechanism that would force freshness is branch-protection *"require branches up to date before merging"*, which re-runs checks against the moved base. dev-flow does not control it and this design must not assume it.

So #48 closes the version instance for the common fast path (full-auto, or a short pause with a subsequent head push) and leaves open precisely the window gap 2 describes — a base move during a `pre-merge` pause — plus the entire *general* class (any future base-relative criterion a design invents, which has no CI check at all). The general gap is real and open. #38's own workaround (Run 7b: re-run the version check locally, immediately before merge) is the shape of the missing pipeline behaviour.

### The shared root

Both gaps are one thing seen twice: **the pipeline has no vocabulary for a check whose verdict is defined at merge time, against the moving world — so it has nowhere to be authored (gap 1) and no one obliged to re-run it (gap 2).** A single construct answers both: a check the plan declares outside its task list, that the merge gate discharges against a fresh `origin/main` before merging.

## Decomposition decision — no split

The gaps are *separable at the symptom* (one could add a merge-gate step without touching checkbox rules, or vice versa) but *coupled at the solution*: fixing gap 1 by saying "such a step is never a task" is incomplete until gap 2 supplies the home and the obligation ("…it lives in the plan's merge-gate section, which the merge gate discharges"), and fixing gap 2 requires the merge gate to know *which* checks to re-run, which is exactly what gap 1's home declares. The issue's hypothesis — "a single fix plausibly answers both" — holds. **One unified design. Not filed as two.**

## Approaches considered

**(A) Document-only — the issue's "do nothing but state the rule."** Add one sentence: merge-time criteria are the orchestrator's job, never a plan task; and require the `pre-merge` halt report to say so. **Rejected.** It forbids the task-box home without providing another, so the base-relative check still has nowhere concrete to live — it stays ad-hoc prose (exactly #38's Run 7b), and "the halt report says re-run it" is the unenforced precondition #38 already wrote and already flagged as insufficient. It does nothing for gap 2's mechanism: the merge gate still re-verifies nothing base-relative. Good as far as it goes for gap 1's *guidance*, but it leaves the load-bearing half of both gaps unaddressed.

**(B) A named, box-free plan section the merge gate discharges — CHOSEN.** Bless what #38 invented ad hoc as first-class: a `## Merge-gate checks` plan section holding prose steps (no `- [ ]` boxes), and a merge-gate obligation to discharge it against a freshly-fetched `origin/main` before merge. Gap 1's home is that section; gap 2's mechanism is the discharge. Its **Execute-exclusion** is correct-by-default: the section is *already* invisible to `task-brief` (which briefs only `## Task N` spans) and, carrying no `- [ ]` boxes, to the resume row's line-anchored count — any box-free section drops out of Execute with nothing for the author to remember. Its **discharge** rests on a narrower contract: the merge gate reads the section by its exact `## Merge-gate checks` heading, so a check filed under a different heading — or never recognised as a merge-time check — is discharged by no one and the gate proceeds silently, along the *same code path* as a legitimately absent section, which the gate cannot and must not distinguish from a misfiled one. That contract is held on the **authoring** side, not the gate: Edit 2 instructs the plan author to use the pinned heading and the plan review is the backstop; there is deliberately no runtime scan of the plan for stray merge-time checks (heavier and more error-prone than the wart). This is still a strict improvement on #38's hand-wired halt-report step — the author files a check under a heading instead of remembering bespoke orchestrator prose — but "correct-by-default" describes the Execute-exclusion; the discharge is correct-by-**contract**. Rationale for choosing it over (A): the durable fix "belongs in `SKILL.md`" (the #38 plan's own conclusion), and the rubric prefers a correct-by-default seam over a manual step each author must remember.

**(C) A second checkbox syntax the Execute-resume row ignores.** The issue's second candidate for gap 1. **Rejected as over-engineering.** It adds a parallel box grammar to a prose spec a model must execute exactly every run, and it buys nothing over a box-free named section: the section already routes around the resume row (which matches `^[[:space:]]*[-*+] \[ \]`) simply by containing no boxes. New grammar, no new capability.

**(D) A general "re-run all the design's success criteria at merge" engine.** The issue's first candidate for gap 2, taken to its widest. **Rejected as over-engineering.** Most success criteria are about the diff, which the merge does not change; re-running them all is waste, and specifying "all criteria, mechanically, at merge" in prose invites a model to re-run things that read the (possibly stripped) design doc. The chosen design re-runs only the narrow declared subset whose verdict actually moves with the world.

**(E) Make the merge gate integrate `origin/main` before merge** (merge/rebase the base in, re-triggering CI). **Rejected.** Integrating `origin/main` pushes a non-strip commit, which **invalidates the marker** (Marker validity) and forces a full re-review on every `pre-merge` resume where the base moved — the exact expensive path the pipeline exists to avoid — even when nothing conflicts. It also changes a deliberate property: the gate today never integrates the base. A local re-check of the narrow declared subset gets the same safety without the re-review.

## The proposed change

Three coordinated edits **in each of the two twins** (six insert/extend sites total). Anchor on the quoted current text, never on line numbers. Keep every added sentence sharp — this text ships into every model invocation of the skill.

Terminology: the coined term is **merge-time check**. Do **not** coin "boundary" — `CONTEXT.md:86` marks it an _Avoid_ synonym (for **Seam**). Refer to the stage explicitly ("at merge time", "Stage 5's merge gate"). `merge-time` currently appears nowhere in the repo (`git grep -in 'merge-time' -- plugins/` is empty), so it collides with nothing.

### Edit 1 — define the merge-time check, in **Execution-complete signal**

**Anchor (both twins):** the paragraph beginning `**Execution-complete signal.**` and ending `… verify via `git log`, tick the boxes, and do not re-implement.` (dev-flow `:165`, worktree `:159`; the two are near-mirrors, differing only in the parenthetical `is not durable pipeline state` vs `dies with the worktree`).

**Append** a short passage stating, in the pipeline's own voice:

- A criterion that **cannot be discharged inside Execute** — because its verdict is defined only at merge time, turning on the current `origin/main` rather than on the branch tip — is a **merge-time check**, and is **never a plan task box**.
- The two failure modes if it is forced into a box, named concretely so a future plan author recognises the temptation: unticked → Execute's exit is unsatisfiable and the resume row re-routes a ready PR back into Execute; ticked → the tick commits after the marker and (under `docs: commit`) invalidates it, routing the resume to a re-review of an already-clean PR.
- Its home is the plan's `## Merge-gate checks` section (Stage 2); Stage 5's merge gate discharges it (Edit 3). The line-anchored task count (`^[[:space:]]*[-*+] \[ \]`) already tolerates this: the section carries no boxes, so it neither counts toward Execute's completion nor trips the resume row.

The passage appended here must be a **substitution image** across the twins (identical after `dev-flow-worktree` → `dev-flow`) — the surrounding paragraph already is, and this passage introduces no worktree-specific content. Success criterion 7 checks it.

### Edit 2 — give the plan author the section, in **Stage 2 — Plan**

**Anchor (both twins):** the bullet beginning `- **Make each `## Task N` section self-sufficient` (dev-flow `:220`, worktree `:214`), the existing plan-authoring instruction. **Add a sibling bullet** directly after it.

The new bullet instructs `writing-plans` (carried in the produce-subagent dispatch, as this bullet already is): a design success criterion that is a **merge-time check** (per Execution-complete — its verdict turns on the current `origin/main`, re-evaluated at merge, not on the branch tip) is placed in a dedicated **`## Merge-gate checks`** section as **prose steps, never `- [ ]` boxes and never a `## Task N`**. Each step must be **self-contained per Command discipline** — it names and validates any git ref it consumes and does not depend on another section — because `task-brief` briefs only `## Task N` spans, so this section is (correctly) invisible to implementers and is executed only by the merge gate. If the design declares no merge-time check, the section is omitted. This doubles as a `writing-plans` self-review criterion: a step that cannot complete in Execute and cannot be given a `## Merge-gate checks` home is a **halt-and-report**, not an extra `## Task N`.

### Edit 3 — discharge the section, by extending **merge-gate step 3**

**Anchor (both twins):** merge-gate **step 3**, the bullet beginning `3. **Consult `stops`**` (dev-flow `:253`, worktree `:247`), ending `… step 1 already halted it.)`. **Extend** this step, and **rename its header** in place from `3. **Consult `stops`**` to `3. **Consult `stops`, then discharge the merge-gate checks**` — a compound header parallel to step 1's `**Push, then confirm the marker**`, so a reader scanning the gate by step header sees the discharge lives here. Renaming the header renumbers nothing (every gate cross-reference names steps by number — `step 1`, `step 4`, `step 5` — never by header); **do not add a numbered step** — that would renumber steps 4/5 and every "step N" cross-reference in the gate, and in the worktree twin the intro's "worktree entry, step 4" refers to *worktree-entry* step 4, a landmine. Placing the discharge inside step 3 is deliberate and correct: step 3 is where the `pre-merge` pause happens and where the design doc is already read at tip **before any strip**, and its stripped-state handling already reads as "in the stripped state there is no doc at tip and this read is not attempted."

The extension states: **after** the stop consultation (so it runs on the resuming, non-paused pass — or immediately, when there is no `pre-merge` stop) and **before** proceeding to the strip, the orchestrator discharges the plan's `## Merge-gate checks` section against a **freshly-fetched `origin/main`**. The shipped prose carries the pinned literal `freshly-fetched` (success criterion 6) and, for the stripped-state clause, the plain literal `this discharge is not attempted` (criterion 10) — both written verbatim, no interior emphasis, so the fixed-string greps match:

- **Absent section — the common case.** A plan with **no `## Merge-gate checks` section** — most plans, and every plan authored before this construct — discharges nothing here and proceeds; an absent section is a **pass, never a halt**, and no fetch runs (so a section-less `commit`-policy run still merges without a base fetch, exactly as before this construct existed).
- **Present section.** `git fetch origin "+refs/heads/<default>:refs/remotes/origin/<default>"` — the explicit refspec (as at the strip-path fetch), not a bare `git fetch origin <default>`, so `origin/<default>` actually refreshes in a single-branch clone; **failure halts and reports**, because a discharge against a base it could not refresh is worthless and the gate is re-entrant so resume retries for free, exactly like step 2's CI-pending halt. Then run each prose step (each a deterministic pass/fail command by Edit 2's authoring rule and Command discipline — a judgment-call step is an Edit-2 authoring violation for the plan review to catch, not something the gate can adjudicate). Any step that fails → **halt and report** the failing check and its remediation, and do **not** merge. (Halt, not in-gate auto-fix: a remediating commit — e.g. a version re-bump — invalidates the marker, so the correct response is the resume routing back through Stage 4's re-review, which the pipeline already owns. Auto-fixing mid-gate would duplicate that logic.) This fetch's halt-on-failure narrows the pre-existing "merges offline under `commit`" property to plans with **no** merge-gate checks — a plan that declares a merge-time check cannot merge without a reachable origin, by the check's own nature, parallel to how the strip-path fetch already halts. Correct, not a regression.
- In the **stripped state** the plan doc is gone at tip and this discharge is not attempted — it ran on the pre-strip pass, exactly as step 3's `stops` read is not attempted there. (Under `docs: commit`, the default and this repo's setting, there is no strip: step 3's discharge is immediately followed by step 4's no-op and step 5's merge, so the check runs against `origin/main` seconds before the merge.)
- One clause naming what this buys: the marker and CI wait certify facts anchored to the branch SHA; this is the only re-verification of facts anchored to the *moving* `origin/main`, and it is what makes the gate's re-entrancy invariant true of the design's criteria and not only of the gate's own five steps. In the **worktree** twin, this discharge — like every git command in that gate — runs from inside the pipeline worktree (the twin's intro already says so).

**Residual, disclosed:** under `docs: strip`, the merge on the stripped re-entry happens after a **full gate re-entry** — the strip commit/push, then step 1's marker re-confirm and step 2's bounded CI wait (up to the ~10-minute cap) — following the pre-strip discharge, a window in which `origin/main` could in principle move again. This is orders of magnitude smaller than the days-long `pre-merge` pause the fix targets (minutes, not days), the strip changes no version, and fully closing it would require branch protection, which is the repo's setting, not the pipeline's. Left as-is, not deferred.

### Version bumps (implementation obligation — number chosen by plan/execute, not here)

Editing this prose is a behaviour change, so per `CLAUDE.md` both manifests bump their `version` (minor segment), and past `origin/main`, not past this branch's base:

- `plugins/dev-flow/.claude-plugin/plugin.json`
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`

Both currently read `2.14.0` / `1.16.0`, equal to `origin/main` (`git show origin/main:…`). The plan/execute stages pick the target and re-check it at merge time; this design does not hardcode a number, because a concurrent branch may publish the next one first. The version-collision guard is itself now CI (`check-version-bump.yml`, #48) **and** — fittingly — the archetypal merge-time check this design generalises: a plan for *this* change should place `python3 scripts/check-version-bump.py origin/main` in its own `## Merge-gate checks` section, dogfooding the construct.

## Assumptions

- **A1.** The `## Merge-gate checks` heading and every load-bearing token below (`merge-time check`, `freshly-fetched`, `` never `- [ ]` boxes ``, `this discharge is not attempted`) are pinned by **this design**; the success criteria grep those exact literals with `git grep -cF`, and the plan reproduces them verbatim. Refining any token is a design change (re-review), not a plan liberty. The heading is a **single pinned contract** carried identically in three places — Edit 2's authoring instruction, Edit 3's gate discharge, and the plan author's own section — with success criterion 5's grep enforcing it across the two `SKILL.md` sites. "Any heading works" holds only for *escaping the Execute resume row* (any heading that is not `## Task N` and carries no `- [ ]` boxes escapes it); it does **not** hold for the *gate discharge*, which matches the heading literally, so a section under any other heading is discharged by no one (see approach B).
- **A2.** The two twins' **Execution-complete signal** paragraphs are near-mirrors today (verified: identical after `dev-flow-worktree` → `dev-flow` except the ledger-scope parenthetical), so Edit 1's appended passage can and must be a clean substitution image. Edits 2 and 3 land in text that is *not* a mechanical mirror (Stage 2 and the merge gate differ between twins — the worktree gate is worktree-driven), so they are hand-mirrored: the success criteria assert the load-bearing tokens appear in both twins, not byte-identity.
- **A3.** `docs: commit` is this repo's setting and the default; the strip path is the minority case, and the residual window it carries (above) is accepted. A run under `docs: strip` still discharges the section on the pre-strip pass.
- **A4.** No file outside the two `SKILL.md` twins describes the merge gate's steps or the plan-checkbox semantics as behaviour (verified: the two `README.md`s and `CONTEXT.md` mention "merge gate"/"pre-merge" only descriptively; `docs/adr` not at all), so no `README.md` or `CONTEXT.md` edit is implied. Whether `CONTEXT.md` should gain a **Merge-time check** glossary entry is a defensible separate question, deferred (A5), not decided here — `CONTEXT.md` is outside this change's file set and concurrently owned.
- **A5.** Follow-up, filed at integration (check first that no equivalent open issue exists): whether `CONTEXT.md` should carry a **Merge-time check** glossary entry, now that the term is load-bearing across both twins and three paragraphs (Execution-complete, Stage 2, the merge gate).
- **A6.** Issue #43 closes on merge; the PR body carries `Closes #43`.

## Success criteria — every item a runnable check

No automated test suite exists in this repo; these are the whole verification surface. Capture `BASE` once against a **freshly-fetched** `origin/main`, validated non-empty, and quote it (Command discipline). Without the fetch, a stale `refs/remotes/origin/main` makes `BASE` an older ancestor than the true fork point, so criterion 3's `"$BASE"..HEAD` diff picks up unrelated commits `origin/main` moved through during a `pre-merge` pause and false-fails — the exact staleness this design fixes at the gate must not defeat its own criteria:

```sh
git fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main" \
  || { echo "fetch failed"; exit 1; }          # same refspec criterion 9 and CI use
BASE=$(git merge-base origin/main HEAD)         # the true fork point, not a stale ancestor
[ -n "$BASE" ] || { echo "BASE empty"; exit 1; }
```

Each content criterion greps a **fixed literal token this design pins** — matched with `git grep -cF` (fixed-strings), so no regex-metacharacter or platform-regex behavior is relied on — and the plan reproduces that token byte-for-byte in the edited files (it does not choose it). `DF` = `plugins/dev-flow/skills/dev-flow/SKILL.md`, `WT` = `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`.

1. **Repo mirror check untouched.** `python3 scripts/check-sync.py` exits 0 and its `mirror pair "adversarial-review"` line is unchanged — this change touches neither member of that mechanically-checked pair.
2. **Marketplace valid.** `claude plugin validate .` exits 0 with exactly **8** `No author information provided` warnings and no errors (the documented pass state).
3. **File scope.** `git diff --stat "$BASE"..HEAD` names only: `DF`, `WT`, the two `plugin.json`s, and paths under `docs/superpowers/` (this design and its plan). Any other path — in particular `CONTEXT.md`, `CLAUDE.md`, `README.md`, or anything under `scripts/` — is a blocker, not a fix to apply.
4. **The coined term landed in both twins.** `git grep -c 'merge-time check' -- "$DF"` ≥ 1 **and** `git grep -c 'merge-time check' -- "$WT"` ≥ 1. (Before this change both are 0 — `git grep -in 'merge-time' -- plugins/` is empty at `BASE`.)
5. **The plan section is named in both twins**, in both the Stage 2 bullet and the merge-gate step: `git grep -c 'Merge-gate checks' -- "$DF"` ≥ 2 **and** the same for `WT` ≥ 2. (Edit 2 names it once, Edit 3 names it once.)
6. **The merge-gate discharge fetches `origin/main` in both twins.** Edit 3's extension of merge-gate `step 3` must contain the pinned literal token `freshly-fetched` (this design coins it for the discharge; `git grep -c freshly-fetched -- plugins/` is 0 at `BASE`). Assert `git grep -cF freshly-fetched -- "$DF"` ≥ 1 **and** ≥ 1 for `WT`. The token is distinctive to Edit 3, so its presence in each twin certifies the discharge prose landed. `git grep -c` cannot confirm *where* a hit sits, so this criterion makes no step-3 position claim — placement is enforced by the anchor Edit 3 names, exactly as criteria 4–5 rely on distinctive tokens rather than line ranges.
7. **Edit 1 is a substitution image across the twins.** Extract the passage Edit 1 appends to the **Execution-complete signal** paragraph from each twin (the text added after the paragraph's existing final sentence, `… tick the boxes, and do not re-implement.`) and assert `wt_passage.replace("dev-flow-worktree", "dev-flow") == df_passage`. That equality is the entire check and is independent of how many plugin tokens the passage holds — it passes iff the two passages are identical after normalizing `dev-flow-worktree` → `dev-flow`. Per A2 the passage introduces no worktree-specific content, so it names neither plugin and the equality reduces to byte-identity; there is deliberately no plugin-token count, because the substitution image already subsumes it (the #38 check counted a token *its* mirrored line contained once; Edit 1's passage contains it zero times — correct, not a defect). (Edits 2 and 3 are hand-mirrored and covered by criteria 4–6 and 10, per A2.)
8. **The merge-gate section is constrained to prose, no boxes, in both twins.** Edit 2's Stage 2 bullet must contain the pinned literal token — the fixed string `` never `- [ ]` boxes `` — which is the load-bearing constraint keeping the `## Merge-gate checks` section clear of Execute's task count and the resume row. Assert, in a fenced block so the backticks survive:

   ```sh
   git grep -cF 'never `- [ ]` boxes' -- "$DF"    # >= 1
   git grep -cF 'never `- [ ]` boxes' -- "$WT"    # >= 1
   ```

   Fixed-strings (`-F`) matches the literal `[ ]` and backticks exactly — no BRE/ERE alternation, so no dependence on the platform's or git build's regex behavior.
9. **Both plugin versions bumped past `origin/main`** — the implementation obligation, and now also CI. After a validated refresh:

   ```sh
   git fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main"   # failure halts; same refspec the CI workflow uses
   python3 scripts/check-version-bump.py origin/main                         # exit 0 iff both touched plugins are ahead
   ```

   Exit 0 is required. This is the same script `.github/workflows/check-version-bump.yml` runs on every PR (#48), so criterion 9 and the CI gate are the same assertion; the design does not name the target numbers, only that both are strictly ahead of `origin/main`.

10. **Edit 3's stripped-state bypass landed, in both twins.** The discharge must be skipped in the stripped state — else a `docs: strip` re-entry reads `## Merge-gate checks` from a plan doc absent at tip and halts under Command discipline. Edit 3's step-3 extension must contain the pinned literal token `this discharge is not attempted` — distinctive to the discharge bypass and distinct from step 3's pre-existing `this read is not attempted` stops clause. Assert `git grep -cF 'this discharge is not attempted' -- "$DF"` ≥ 1 **and** ≥ 1 for `WT`.

## Spec self-review

- **Placeholders / TBDs:** none. Every content criterion greps a **fixed literal token this design pins** — `merge-time check`, `Merge-gate checks`, `freshly-fetched`, `` never `- [ ]` boxes ``, `this discharge is not attempted` — with `git grep -cF`, so each grep is runnable verbatim as written here (each token verified absent from `plugins/` at `BASE`, so every check is a real 0→≥1). The plan reproduces these tokens byte-for-byte; it does not choose them, and altering one is a design change, not a plan edit. The only value the implementation supplies is the target version numbers (criterion 9), deliberately left to plan/execute per `CLAUDE.md`.
- **Internal consistency:** Edit 1 defines the merge-time check; Edit 2 gives it a home; Edit 3 discharges that home. The resume-row and `task-brief` facts the design leans on (`^[[:space:]]*[-*+] \[ \]`; briefs only `## Task N`) are quoted from the current files, the "box-free section" requirement (criterion 8) is what keeps the new section clear of both, and Edit 3's stripped-state bypass is guarded by criterion 10.
- **Scope / no gold-plating:** three edits per twin, plus two version bumps. No box syntax (C), no criteria engine (D), no base integration (E), no `CONTEXT.md`/`README.md`/`scripts/` change. The strip residual is disclosed and accepted rather than engineered away.
- **Ambiguity in the criteria:** each content criterion names a fixed literal token this design pins and matches it with `git grep -cF`, so no platform-regex behavior is relied on and there is no phrasing the plan is free to vary; the two mechanical-mirror exemptions (A2) are stated, so a reviewer does not expect byte-identity where the twins legitimately diverge (Stage 2, the merge gate).
- **Measurements are derived, not typed:** current versions (`2.14.0`/`1.16.0`, equal to `origin/main`) and the "`merge-time` appears nowhere" fact were printed by the commands named beside them, at `BASE`; no number appears that a command did not show.
- **Terminology:** the design coins `merge-time check` (collides with nothing) and deliberately avoids `boundary` (a `CONTEXT.md` _Avoid_ synonym). It reuses `merge gate`, `marker`, `strip`, and `Command discipline` in their established senses.
