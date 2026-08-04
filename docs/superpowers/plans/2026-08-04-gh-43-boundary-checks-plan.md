---
dev-flow:
  slug: gh-43-boundary-checks
  spec: docs/superpowers/specs/2026-08-04-gh-43-boundary-checks-design.md
---

# gh-43 merge-time checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce one construct — a *merge-time check* — into both dev-flow pipeline `SKILL.md` twins, giving it one home to be authored (the plan's `## Merge-gate checks` section) and one place to be discharged (Stage 5's merge gate against a freshly-fetched `origin/main`), then bump both plugins.

**Architecture:** Three coordinated prose edits in *each* of the two hand-mirrored `SKILL.md` twins (six sites), plus a version bump of each plugin manifest. There is no code or test surface — the correctness surface is the edited Markdown, verified entirely by fixed-string greps and structural assertions. Edit 1 (a substitution image) and Edit 2 name neither plugin and are therefore byte-identical across the twins; Edit 3's extension diverges by exactly one worktree clause because the worktree gate is worktree-driven.

**Tech Stack:** Markdown (the two `SKILL.md` files), JSON (the two `plugin.json` manifests), `git grep -cF` / `python3` for verification, `scripts/check-version-bump.py`.

## Global Constraints

- **Edit BOTH twins for every prose edit, and verify BOTH.** The two files are **hand-mirrored** — `scripts/check-sync.py` does **not** check this pair (it checks only the adversarial-review pair and the manifest descriptions), so nothing mechanical catches an edit applied to one twin and missed on the other. `DF` = `plugins/dev-flow/skills/dev-flow/SKILL.md`; `WT` = `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`.
- **The five pinned literal tokens below are fixed by the design; reproduce them byte-for-byte and never paraphrase.** The success criteria grep them with `git grep -cF` (fixed strings). Refining any token is a *design* change, not a plan/execute liberty.

  ```text
  merge-time check
  Merge-gate checks
  freshly-fetched
  never `- [ ]` boxes
  this discharge is not attempted
  ```

- **Anchor on quoted current text, never on line numbers.** Line numbers in this plan are advisory; find the quoted anchor string.
- **The verbatim prose blocks in Tasks 1–3 are load-bearing and contract-pinned.** Insert each block exactly as written here — no rewording, no re-wrapping, no smart-quote substitution. If for any reason you cannot read a block from this plan file, **stop and report**; never reconstruct or substitute it. The plan file is at `/Users/taylor/dev/claude-plugins/docs/superpowers/plans/2026-08-04-gh-43-boundary-checks-plan.md`.
- **Version bump:** both `plugins/dev-flow/.claude-plugin/plugin.json` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json`, **minor segment**, bumped **strictly past `origin/main`** (not past this branch's base). Re-derive the target from `git show origin/main:…` at execute time — a concurrent branch may have published the next number first — and confirm with `python3 scripts/check-version-bump.py origin/main`.
- **File scope — a blocker if violated.** The whole change may touch ONLY: `DF`, `WT`, the two `plugin.json`s, and paths under `docs/superpowers/` (this design, this plan, and the plan's checkbox commits). Any other path — `CONTEXT.md`, `CLAUDE.md`, `README.md`, anything under `scripts/` — is a defect to remove, not a fix to apply.
- **Measurements are derived, not typed.** Every version number or count a step states must be one a command in that step printed. Capture, validate non-empty, and quote any git ref a later command consumes (Command discipline).

---

### Task 1: Edit 1 — define the merge-time check in *Execution-complete signal* (both twins)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (DF) — the `**Execution-complete signal.**` paragraph
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (WT) — the `**Execution-complete signal.**` paragraph

**Anchor (identical logical site in both twins).** A single-line paragraph that begins `**Execution-complete signal.**` and ends with the sentence `… verify via `git log`, tick the boxes, and do not re-implement.` The two twins differ only in an earlier ledger parenthetical (`is not durable pipeline state` in DF vs `dies with the worktree` in WT); the trailing sentence you anchor on — `tick the boxes, and do not re-implement.` — is byte-identical in both.

**The edit.** At the very end of that paragraph line, immediately after `do not re-implement.`, append the passage below — keeping it on the **same physical line** (same paragraph). The block begins with a single leading space that separates it from `re-implement.`. Insert the **same** passage into DF and into WT: it names neither plugin, so the two are byte-identical, which is exactly what makes it a substitution image (success criterion 7).

**APPEND-PASSAGE — verbatim, identical for DF and WT (note the leading space):**

```text
 A criterion that **cannot be discharged inside Execute** — because its verdict is defined only at merge time, turning on the current `origin/main` rather than on the branch tip — is a **merge-time check**, and is **never a plan task box**. Forced into a box it fails two ways: left **unticked**, Execute's exit is unsatisfiable and the resume row (which matches `^[[:space:]]*[-*+] \[ \]`, evaluated above the marker rows) re-routes an already-reviewed, marker-and-CI-ready PR back into Execute; **ticked** where its step actually runs, the tick is a commit landing after the review marker and (under `docs: commit`) invalidates it, routing the resume to a re-review of an already-clean PR. Its home is instead the plan's `## Merge-gate checks` section (Stage 2 — Plan), which Stage 5's merge gate discharges before merge. The line-anchored task count already tolerates this: that section carries no `- [ ]` boxes, so it neither counts toward Execute's completion nor trips the resume row.
```

- [x] **Step 1: Locate the DF anchor**

Read `plugins/dev-flow/skills/dev-flow/SKILL.md` and find the line beginning `**Execution-complete signal.**`. Confirm it ends with `do not re-implement.` (nothing after it on the line).

- [x] **Step 2: Append the passage to DF**

Append the APPEND-PASSAGE block (with its leading space) to the end of that line, keeping it on the same line. Do not start a new paragraph.

- [x] **Step 3: Locate the WT anchor and append the identical passage**

Read `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, find its `**Execution-complete signal.**` line (ends with `do not re-implement.`), and append the **identical** APPEND-PASSAGE block to the end of that line.

- [x] **Step 4: Verify the coined term landed in both twins (criterion 4)**

Run:

```sh
DF=plugins/dev-flow/skills/dev-flow/SKILL.md
WT=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -cF 'merge-time check' -- "$DF"   # expect >= 1
git grep -cF 'merge-time check' -- "$WT"   # expect >= 1
```

Expected: each prints a count ≥ 1.

- [x] **Step 5: Verify Edit 1 is a substitution image (criterion 7)**

Run:

```sh
python3 - <<'PY'
def appended(path):
    for line in open(path, encoding='utf-8'):
        if line.startswith('**Execution-complete signal.**'):
            assert 'do not re-implement.' in line, 'anchor sentence missing in ' + path
            return line.split('do not re-implement.', 1)[1].rstrip('\n')
    raise SystemExit('Execution-complete paragraph not found in ' + path)

df = appended('plugins/dev-flow/skills/dev-flow/SKILL.md')
wt = appended('plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md')
assert df, 'nothing appended in DF'
assert wt.replace('dev-flow-worktree', 'dev-flow') == df, 'Edit 1 is NOT a substitution image'
assert 'merge-time check' in df, 'pinned token missing'
print('Edit 1 OK: substitution image;', len(df), 'chars appended')
PY
```

Expected: prints `Edit 1 OK: …`. Any assertion failure means the two passages diverged — fix and re-run.

- [x] **Step 6: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "gh-43: Edit 1 — define the merge-time check in Execution-complete signal (both twins)"
```

---

### Task 2: Edit 2 — give the plan author the `## Merge-gate checks` section, in Stage 2 (both twins)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (DF) — Stage 2 — Plan
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (WT) — Stage 2 — Plan

**Anchor (byte-identical in both twins).** The existing plan-authoring bullet, a single line beginning:

`- **Make each `## Task N` section self-sufficient — instruct `writing-plans` so.**`

and ending `… **halt and report** any out-of-section reference that cannot be given an in-section pointer rather than ship the plan.` The next line after it is the bullet `- The **orchestrator** invokes `dev-flow…:adversarial-review` (mode: `plan`)…`.

**The edit.** Insert the NEW-BULLET below as its own new line **directly after** the anchor bullet (and before the `- The **orchestrator** invokes …` bullet). Insert the **same** bullet into DF and into WT — it names neither plugin, so the two are byte-identical (this was confirmed against both files; the surrounding anchor bullet is itself byte-identical between the twins).

**NEW-BULLET — verbatim, identical for DF and WT:**

```text
- **Place a merge-time check in a `## Merge-gate checks` section, never a task.** A design success criterion that is a **merge-time check** (per *Execution-complete signal* — its verdict turns on the current `origin/main`, re-evaluated at merge, not on the branch tip) goes there as prose steps, never `- [ ]` boxes and never a `## Task N`. Each step must be self-contained per Command discipline — it names and validates any git ref it consumes and depends on no other section — because `task-brief` briefs only `## Task N` spans, so the section is (correctly) invisible to implementers and is discharged only by Stage 5's merge gate. If the design declares no merge-time check, the section is omitted. This doubles as a `writing-plans` self-review criterion: a step that cannot complete in Execute and cannot be given such a home is a **halt-and-report**, not an extra `## Task N`.
```

- [x] **Step 1: Locate the DF anchor bullet**

Read `plugins/dev-flow/skills/dev-flow/SKILL.md`; find the line beginning `- **Make each `## Task N` section self-sufficient`. Note the bullet directly after it (`- The **orchestrator** invokes …`).

- [x] **Step 2: Insert the new bullet into DF**

Insert the NEW-BULLET as a new line between the anchor bullet and the `- The **orchestrator** invokes …` bullet.

- [x] **Step 3: Insert the identical bullet into WT**

Read `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`; find its byte-identical `- **Make each `## Task N` section self-sufficient` bullet, and insert the **identical** NEW-BULLET as a new line directly after it.

- [x] **Step 4: Verify the box-free constraint token landed (criterion 8)**

Run (fenced so the backticks and `[ ]` survive literally):

```sh
DF=plugins/dev-flow/skills/dev-flow/SKILL.md
WT=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -cF 'never `- [ ]` boxes' -- "$DF"   # expect >= 1
git grep -cF 'never `- [ ]` boxes' -- "$WT"   # expect >= 1
```

Expected: each prints a count ≥ 1.

- [x] **Step 5: Verify the section is named in both twins**

Run:

```sh
DF=plugins/dev-flow/skills/dev-flow/SKILL.md
WT=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -cF 'Merge-gate checks' -- "$DF"   # 2 now (Edit 1 named it + Edit 2); 3 after Edit 3 (criterion 5)
git grep -cF 'Merge-gate checks' -- "$WT"   # 2 now (Edit 1 named it + Edit 2); 3 after Edit 3 (criterion 5)
git grep -cF 'merge-time check' -- "$DF"    # expect >= 1
git grep -cF 'merge-time check' -- "$WT"    # expect >= 1
```

Expected: both `merge-time check` counts ≥ 1; both `Merge-gate checks` counts are **2** here — Edit 1's appended passage already names the section and Edit 2 names it again — so criterion 5's ≥ 2 aggregate is already satisfied at this point (Edit 3 raises it to 3, re-verified in Task 5).

- [x] **Step 6: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "gh-43: Edit 2 — plan author's ## Merge-gate checks section, in Stage 2 (both twins)"
```

---

### Task 3: Edit 3 — discharge the section by extending merge-gate step 3, and rename its header (both twins)

**Files:**
- Modify: `plugins/dev-flow/skills/dev-flow/SKILL.md` (DF) — Stage 5, merge-gate step 3
- Modify: `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (WT) — Stage 5, merge-gate step 3

**Anchor (step 3 is byte-identical in both twins).** The merge-gate list item, a single line beginning `3. **Consult `stops`**` and ending `… step 1 already halted it.)`. The full current line is:

`3. **Consult `stops`** from the design doc's front-matter at tip; a `pre-merge` stop pauses **here**, with the testing note — before any strip, so a halted branch is always intact and fully resumable with both docs at tip. In the stripped state there is no doc at tip and this read is not attempted: the recorded stops are empty by the stripped-state rule (Docs policy) — proceed, never halt. (A doc-less tip *without* the trailer cannot reach this step; step 1 already halted it.)`

This edit has **two parts**, applied to that one line in **each** twin. **Do not add a numbered step** and do not renumber steps 4/5 — every gate cross-reference names steps by number.

**Part A — rename the header (identical in both twins).** Step 1's header is a period-terminated compound (`**Push, then confirm the marker.**`) whose body then restates the verbs; make step 3 parallel. Replace the exact substring

`3. **Consult `stops`** from`

with

`3. **Consult `stops`, then discharge the merge-gate checks.** Consult `stops` from`

(That is: extend the bold lead to a compound, close it with a period, and restate `Consult `stops`` to keep the following clause grammatical — the rest of the sentence, `from the design doc's front-matter at tip; …`, is preserved verbatim. The design's directive "rename the header to a compound parallel to step 1" is met exactly by step 1's own shape: a period-terminated bold label followed by a body that restates the verbs.)

**Part B — append the discharge extension** to the **end** of that same step-3 line, immediately after `step 1 already halted it.)`, on the same line. DF gets DF-EXTENSION; WT gets WT-EXTENSION (which is DF-EXTENSION plus one trailing worktree clause — the ONLY twin divergence in this edit, because the Stage-5 gate runs its git from inside the pipeline worktree, as WT's Stage-5 intro already states).

**DF-EXTENSION — verbatim (note the leading space):**

```text
 Then, after that stop consultation — on the resuming, non-paused pass, or immediately when no `pre-merge` stop is recorded — and **before** proceeding to step 4's strip, discharge the plan's `## Merge-gate checks` section against a **freshly-fetched** `origin/main`. A plan with **no** such section — most plans, and every plan authored before this construct — discharges nothing and proceeds: an absent section is a **pass, never a halt**, and no fetch runs, so a section-less `commit`-policy run still merges without a base fetch, exactly as before. When the section **is** present, first refresh the base with the explicit refspec — `git fetch origin "+refs/heads/<default>:refs/remotes/origin/<default>"`, as the strip-path fetch uses, never a bare `git fetch origin <default>` that leaves `origin/<default>` unresolvable in a single-branch clone — and **halt and report on fetch failure**, because a discharge against a base it could not refresh is worthless and the gate is re-entrant, so resume retries for free, exactly like step 2's CI-pending halt. Then run each of the section's prose steps in order (each a deterministic pass/fail command by Stage 2's authoring rule); **any step that fails → halt and report** the failing check and its remediation, and do **not** merge — a remediating commit (e.g. a version re-bump) invalidates the marker, so the correct response is the resume routing back through Stage 4's re-review, which the pipeline already owns, never an in-gate auto-fix. In the stripped state the plan doc is gone at tip and this discharge is not attempted — it ran on the pre-strip pass, exactly as the `stops` read above is not attempted there. This is the gate's only re-verification of a fact anchored to the *moving* `origin/main` rather than to the branch SHA that the marker and step 2's CI wait already certify, and it is what makes the gate's re-entrancy invariant true of the design's criteria and not only of the gate's own five steps.
```

**WT-EXTENSION — verbatim (DF-EXTENSION, then one more sentence appended at the very end):**

```text
 Then, after that stop consultation — on the resuming, non-paused pass, or immediately when no `pre-merge` stop is recorded — and **before** proceeding to step 4's strip, discharge the plan's `## Merge-gate checks` section against a **freshly-fetched** `origin/main`. A plan with **no** such section — most plans, and every plan authored before this construct — discharges nothing and proceeds: an absent section is a **pass, never a halt**, and no fetch runs, so a section-less `commit`-policy run still merges without a base fetch, exactly as before. When the section **is** present, first refresh the base with the explicit refspec — `git fetch origin "+refs/heads/<default>:refs/remotes/origin/<default>"`, as the strip-path fetch uses, never a bare `git fetch origin <default>` that leaves `origin/<default>` unresolvable in a single-branch clone — and **halt and report on fetch failure**, because a discharge against a base it could not refresh is worthless and the gate is re-entrant, so resume retries for free, exactly like step 2's CI-pending halt. Then run each of the section's prose steps in order (each a deterministic pass/fail command by Stage 2's authoring rule); **any step that fails → halt and report** the failing check and its remediation, and do **not** merge — a remediating commit (e.g. a version re-bump) invalidates the marker, so the correct response is the resume routing back through Stage 4's re-review, which the pipeline already owns, never an in-gate auto-fix. In the stripped state the plan doc is gone at tip and this discharge is not attempted — it ran on the pre-strip pass, exactly as the `stops` read above is not attempted there. This is the gate's only re-verification of a fact anchored to the *moving* `origin/main` rather than to the branch SHA that the marker and step 2's CI wait already certify, and it is what makes the gate's re-entrancy invariant true of the design's criteria and not only of the gate's own five steps. Like every git command in this gate, this fetch and each discharged step run from inside the pipeline worktree (worktree entry, step 4).
```

- [x] **Step 1: Rename step 3's header in DF (Part A)**

In `plugins/dev-flow/skills/dev-flow/SKILL.md`, replace the exact substring `3. **Consult `stops`** from` with `3. **Consult `stops`, then discharge the merge-gate checks.** Consult `stops` from`. Leave the remainder of the line unchanged.

- [x] **Step 2: Append DF-EXTENSION to step 3 in DF (Part B)**

Append the DF-EXTENSION block (leading space included) to the end of that same step-3 line, immediately after `step 1 already halted it.)`. Keep it on the same line.

- [x] **Step 3: Rename step 3's header in WT (Part A)**

In `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, apply the **identical** header replacement (`3. **Consult `stops`** from` → `3. **Consult `stops`, then discharge the merge-gate checks.** Consult `stops` from`).

- [x] **Step 4: Append WT-EXTENSION to step 3 in WT (Part B)**

Append the **WT-EXTENSION** block (the one ending with the pipeline-worktree sentence) to the end of WT's step-3 line, immediately after `step 1 already halted it.)`.

- [x] **Step 5: Verify the discharge tokens landed (criteria 6 and 10) and the header renamed**

Run:

```sh
DF=plugins/dev-flow/skills/dev-flow/SKILL.md
WT=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -cF 'freshly-fetched' -- "$DF"                       # criterion 6, expect >= 1
git grep -cF 'freshly-fetched' -- "$WT"                       # criterion 6, expect >= 1
git grep -cF 'this discharge is not attempted' -- "$DF"       # criterion 10, expect >= 1
git grep -cF 'this discharge is not attempted' -- "$WT"       # criterion 10, expect >= 1
git grep -cF 'Consult `stops`, then discharge the merge-gate checks' -- "$DF"  # header, expect >= 1
git grep -cF 'Consult `stops`, then discharge the merge-gate checks' -- "$WT"  # header, expect >= 1
```

Expected: every count ≥ 1.

- [x] **Step 6: Verify the old header string is gone (nothing else changed there)**

Run:

```sh
DF=plugins/dev-flow/skills/dev-flow/SKILL.md
WT=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -qF '**Consult `stops`** from the design' -- "$DF" && { echo "FAIL: old header still in DF"; exit 1; } || echo "OK: old header gone from DF"
git grep -qF '**Consult `stops`** from the design' -- "$WT" && { echo "FAIL: old header still in WT"; exit 1; } || echo "OK: old header gone from WT"
```

Expected: `OK: old header gone from DF` and `OK: old header gone from WT` (the old bold header no longer precedes `from the design`). A `FAIL` line with a non-zero exit means the rename did not land.

- [x] **Step 7: Confirm the WT-only worktree clause is present in WT and absent from DF**

Run:

```sh
DF=plugins/dev-flow/skills/dev-flow/SKILL.md
WT=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git grep -qF 'this fetch and each discharged step run from inside the pipeline worktree' -- "$WT" && echo "OK: worktree clause present in WT" || { echo "FAIL: worktree clause missing from WT"; exit 1; }
git grep -qF 'this fetch and each discharged step run from inside the pipeline worktree' -- "$DF" && { echo "FAIL: worktree clause present in DF"; exit 1; } || echo "OK: worktree clause absent from DF"
```

Expected: `OK: worktree clause present in WT` and `OK: worktree clause absent from DF` — the sole WT-only divergence is in WT and not in DF. Any `FAIL` line (non-zero exit) means the clause is missing from WT or leaked into DF.

- [x] **Step 8: Commit**

```bash
git add plugins/dev-flow/skills/dev-flow/SKILL.md plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
git commit -m "gh-43: Edit 3 — discharge ## Merge-gate checks at merge-gate step 3 (both twins)"
```

---

### Task 4: Version bumps — both plugin manifests, minor segment, past `origin/main`

**Files:**
- Modify: `plugins/dev-flow/.claude-plugin/plugin.json` — `version`
- Modify: `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `version`

**Why.** Editing the skills' behavior is a behavior change, so `CLAUDE.md` requires a `version` bump on each touched plugin. The bump must land **past `origin/main`**, not past this branch's base — a concurrent branch may have published the next number, and a byte-identical version line merges without conflict. This obligation is now also CI (`.github/workflows/check-version-bump.yml`, which runs `python3 scripts/check-version-bump.py origin/main`).

Derive the target from `origin/main` at execute time — the next **minor** past whatever Step 1 prints for each plugin — and **do not type a number a command did not print**, because a concurrent merge may have advanced `origin/main` since this plan was written. (At `BASE`, `origin/main` published `2.14.0` (dev-flow) and `1.16.0` (dev-flow-worktree); absent a concurrent merge the target is therefore `2.15.0` / `1.17.0` — an illustration of the derivation, not a value to hardcode.)

- [x] **Step 1: Fetch and read the current `origin/main` versions**

```sh
git fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main" \
  || { echo "fetch failed"; exit 1; }
git show origin/main:plugins/dev-flow/.claude-plugin/plugin.json \
  | python3 -c "import json,sys; print('dev-flow', json.load(sys.stdin)['version'])"
git show origin/main:plugins/dev-flow-worktree/.claude-plugin/plugin.json \
  | python3 -c "import json,sys; print('dev-flow-worktree', json.load(sys.stdin)['version'])"
```

Record the two printed versions. The new versions are each the next **minor** past the printed value (e.g. `2.14.0 → 2.15.0`, `1.16.0 → 1.17.0`).

- [x] **Step 2: Set the new version in `plugins/dev-flow/.claude-plugin/plugin.json`**

Edit the `"version"` field to the next minor past the printed dev-flow version (e.g. `2.15.0`). Change nothing else in the file — in particular, leave `description` untouched (it is checked against the marketplace by `check-sync.py`).

- [x] **Step 3: Set the new version in `plugins/dev-flow-worktree/.claude-plugin/plugin.json`**

Edit the `"version"` field to the next minor past the printed dev-flow-worktree version (e.g. `1.17.0`). Change nothing else.

- [x] **Step 4: Confirm both are ahead of `origin/main` (criterion 9)**

```sh
git fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main" \
  || { echo "fetch failed"; exit 1; }
python3 scripts/check-version-bump.py origin/main   # exit 0 iff both touched plugins are ahead
echo "exit=$?"
```

Expected: exit 0. If it fails, a concurrent merge took your target — re-read `origin/main` (Step 1) and bump both past it, then re-run.

- [x] **Step 5: Commit**

```bash
git add plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
git commit -m "gh-43: bump dev-flow and dev-flow-worktree (merge-time-check behavior change)"
```

---

### Task 5: Full success-criteria verification sweep (all 10 criteria + scope proof)

This task runs the design's entire correctness surface — there is no automated test suite. It changes no files; its deliverable is "every check passes." If any check fails, fix the responsible task's output and re-run this sweep.

**Capture `BASE` once against a freshly-fetched `origin/main`, validated non-empty, and quote it** (Command discipline — without the fetch a stale `origin/main` makes `BASE` an older ancestor and criterion 3 false-fails):

```sh
git fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main" \
  || { echo "fetch failed"; exit 1; }
BASE=$(git merge-base origin/main HEAD)
[ -n "$BASE" ] || { echo "BASE empty"; exit 1; }
DF=plugins/dev-flow/skills/dev-flow/SKILL.md
WT=plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md
echo "BASE=$BASE"
```

- [x] **Step 1: Criterion 1 — repo mirror check untouched**

```sh
python3 scripts/check-sync.py; echo "exit=$?"
```

Expected: exit 0; the `mirror pair "adversarial-review"` line is unchanged (this change touches neither member of that pair).

- [x] **Step 2: Criterion 2 — marketplace valid**

```sh
out=$(claude plugin validate . 2>&1); rc=$?
printf '%s\n' "$out" | tail -20
warns=$(printf '%s\n' "$out" | grep -cF 'No author information provided')
[ "$rc" -eq 0 ]    || { echo "FAIL: validate exited $rc (errors present)"; exit 1; }
[ "$warns" -eq 8 ] || { echo "FAIL: expected 8 author warnings, got $warns"; exit 1; }
echo "criterion 2 OK: validate exit 0, $warns author warnings, no errors"
```

Expected: exits 0 with exactly **8** `No author information provided` warnings and no errors (the documented pass state).

- [x] **Step 3: Criterion 3 — file scope**

```sh
git diff --name-only "$BASE"..HEAD \
  | grep -vE '^(plugins/dev-flow/skills/dev-flow/SKILL\.md|plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL\.md|plugins/dev-flow/\.claude-plugin/plugin\.json|plugins/dev-flow-worktree/\.claude-plugin/plugin\.json|docs/superpowers/)' \
  && { echo "SCOPE VIOLATION (paths above are out of scope)"; exit 1; } || echo "scope OK"
```

Expected: `scope OK` (the `grep -vE` prints nothing and exits non-zero). Any printed path — `CONTEXT.md`, `CLAUDE.md`, `README.md`, `scripts/*` — is a blocker.

- [x] **Step 4: Criterion 4 — the coined term landed in both twins**

```sh
git grep -cF 'merge-time check' -- "$DF"   # >= 1
git grep -cF 'merge-time check' -- "$WT"   # >= 1
```

- [x] **Step 5: Criterion 5 — the plan section is named ≥ 2× in each twin**

```sh
git grep -cF 'Merge-gate checks' -- "$DF"  # criterion 5 needs >= 2; actually 3 (Edit 1 + Edit 2 + Edit 3)
git grep -cF 'Merge-gate checks' -- "$WT"  # criterion 5 needs >= 2; actually 3
```

- [x] **Step 6: Criterion 6 — the discharge fetches a freshly-fetched base, in both twins**

```sh
git grep -cF 'freshly-fetched' -- "$DF"    # >= 1
git grep -cF 'freshly-fetched' -- "$WT"    # >= 1
```

- [x] **Step 7: Criterion 7 — Edit 1 is a substitution image across the twins**

```sh
python3 - <<'PY'
def appended(path):
    for line in open(path, encoding='utf-8'):
        if line.startswith('**Execution-complete signal.**'):
            assert 'do not re-implement.' in line, 'anchor sentence missing in ' + path
            return line.split('do not re-implement.', 1)[1].rstrip('\n')
    raise SystemExit('Execution-complete paragraph not found in ' + path)
df = appended('plugins/dev-flow/skills/dev-flow/SKILL.md')
wt = appended('plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md')
assert df and wt, 'empty append'
assert wt.replace('dev-flow-worktree', 'dev-flow') == df, 'Edit 1 is NOT a substitution image'
print('criterion 7 OK')
PY
```

Expected: `criterion 7 OK`.

- [x] **Step 8: Criterion 8 — the section is constrained to prose, no boxes, in both twins**

```sh
git grep -cF 'never `- [ ]` boxes' -- "$DF"   # >= 1
git grep -cF 'never `- [ ]` boxes' -- "$WT"   # >= 1
```

- [x] **Step 9: Criterion 9 — both plugin versions bumped past `origin/main`**

```sh
git fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main" \
  || { echo "fetch failed"; exit 1; }
python3 scripts/check-version-bump.py origin/main; echo "exit=$?"
```

Expected: exit 0.

- [x] **Step 10: Criterion 10 — Edit 3's stripped-state bypass landed, in both twins**

```sh
git grep -cF 'this discharge is not attempted' -- "$DF"   # >= 1
git grep -cF 'this discharge is not attempted' -- "$WT"   # >= 1
```

- [x] **Step 11: Always-check — nothing beyond the intended edits changed**

Confirm the removed old header is gone and eyeball the diff for exactly the four intended hunks per SKILL (Edit 1 append, Edit 2 bullet, Edit 3 header rename + extension) plus the two `version` lines — no other lines:

```sh
git grep -qF '**Consult `stops`** from the design' -- "$DF" && { echo "FAIL: old header still in DF"; exit 1; } || echo "OK: old header gone from DF"
git grep -qF '**Consult `stops`** from the design' -- "$WT" && { echo "FAIL: old header still in WT"; exit 1; } || echo "OK: old header gone from WT"
git diff "$BASE"..HEAD -- "$DF" "$WT" \
  plugins/dev-flow/.claude-plugin/plugin.json \
  plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

Expected: both greps print `OK: old header gone …` (a `FAIL` line with a non-zero exit means the old header survived); the diff shows only the intended insertions/header-rename in each twin and the single `version` line change in each manifest. (This change carries no fenced replacement blocks in the *design*, so the `scripts/design_blocks.py` re-read check does not apply; the verbatim block source of truth is this plan, which the implementers insert without paraphrase.)

- [x] **Step 12: Record the sweep result**

No commit — this task asserts, it does not change files. If every check above passed, the correctness surface is green.

---

## Merge-gate checks

*(This section is **not** a `## Task N` and carries **no `- [ ]` boxes** — it is the very construct this change introduces. Per Edits 1–3, once the new behavior ships it is invisible to `task-brief` and the Execute resume row, and Stage 5's merge gate discharges it against a freshly-fetched `origin/main` immediately before merge. **The currently-installed dev-flow is v2.14.0 and does NOT yet auto-discharge this section**, so until the new behavior ships, discharge it **by hand at the pre-merge / merge boundary** — that manual step is exactly issue #43's gap, and running it here is the point of dogfooding.)*

**Check — both plugin versions are still ahead of `origin/main`.** A concurrent PR may merge this change's target version while this branch pauses at `pre-merge`; the verdict turns on the *current* `origin/main`, so it must be re-run at merge, not just at plan/execute time. Self-contained (Command discipline):

```sh
git fetch --no-tags origin "+refs/heads/main:refs/remotes/origin/main" \
  || { echo "fetch failed"; exit 1; }
python3 scripts/check-version-bump.py origin/main   # exit 0 iff both touched plugins are ahead
echo "exit=$?"
```

If it exits non-zero, a concurrent merge took the target version. Remediate (do **not** merge): re-read each plugin's published version —

```sh
git show origin/main:plugins/dev-flow/.claude-plugin/plugin.json \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
git show origin/main:plugins/dev-flow-worktree/.claude-plugin/plugin.json \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
```

— bump both `plugins/dev-flow/.claude-plugin/plugin.json` and `plugins/dev-flow-worktree/.claude-plugin/plugin.json` to the next minor past what it prints, commit, push, and re-run the check above until it exits 0. (Per the pipeline: a version re-bump is a new commit that invalidates the review marker, so the correct route is back through the PR re-review the pipeline already owns — never an in-gate edit.)

---

## Spec coverage (plan self-review — not a task)

- **Edit 1** → Task 1; criteria **4** (Task 1 Step 4 / Task 5 Step 4) and **7** (Task 1 Step 5 / Task 5 Step 7).
- **Edit 2** → Task 2; criteria **8** (Task 2 Step 4 / Task 5 Step 8) and **5** (Task 2 Step 5 / Task 5 Step 5).
- **Edit 3** → Task 3; criteria **6** (Task 3 Step 5 / Task 5 Step 6), **10** (Task 3 Step 5 / Task 5 Step 10), header rename + old-header-gone always-check (Task 3 Steps 5–7 / Task 5 Step 11), and the WT-only worktree-clause divergence (Task 3 Step 7).
- **Version bumps** → Task 4; criterion **9** (Task 4 Step 4 / Task 5 Step 9).
- **Criteria 1, 2, 3** (mirror check, marketplace valid, file scope) → Task 5 Steps 1–3.
- **`## Merge-gate checks` dogfood** → the box-free section above, discharged manually at the pre-merge boundary until the new behavior ships.
- **Mirror discipline:** every prose task (1–3) edits and verifies BOTH twins; Edit 1 and Edit 2 are byte-identical across twins (name neither plugin), Edit 3 diverges by exactly one WT worktree clause (verified in Task 3 Step 7).
