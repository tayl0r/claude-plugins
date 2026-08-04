---
dev-flow:
  slug: gh-45-plan-cross-task-refs
  stops: [post-design]
  docs: commit
---

# gh-45: a plan whose tasks reference material outside their own `## Task N` section must carry the resolver inside that section

## Summary

dev-flow's Stage 2 produces a plan by dispatching `superpowers:writing-plans`, then executes it in Stage 3 through `superpowers:subagent-driven-development` (SDD). SDD briefs each implementer from `scripts/task-brief PLAN_FILE N`, whose `awk` hands the implementer **only** the text of that one `## Task N` section, with **no plan-file path**. So any cross-task reference a plan writes — a shared `§V` verification-block ID, "Task 1 -> Step 4", "the table above" — is a bare label the implementer cannot resolve from what it was handed. Two prior plans in this repo hit this seam and answered it two different ways, one of which is provably invisible to the implementer. This design writes down one rule, in dev-flow's own Stage 2 guidance, that places the resolver where the brief actually carries it.

The fix is a new **Stage 2 — Plan** bullet, added identically to both mirrored pipeline `SKILL.md` files, instructing the `writing-plans` subagent to make every `## Task N` section self-sufficient (the bullet doubles as a plan self-review criterion). It is paired with a one-line sharpening of the `adversarial-review` **plan-mode reviewer row** — in the machine-checked `adversarial-review/SKILL.md` pair — so the review's existing *"executable by a fresh context-free subagent"* check models what `task-brief` actually hands an implementer, giving the rule an **independent** backstop against a silent failure. One conceptual change, two edit sites.

## The confirmed mechanism (not re-derived here — see facts)

- `superpowers:writing-plans`, `subagent-driven-development`, `scripts/task-brief`, and `implementer-prompt.md` are **external superpowers-plugin artifacts**, not in this repo, and cannot be edited by this change. Confirmed: `find . -iname '*task-brief*'` returns nothing (exit 0, no output).
- `task-brief` extracts only the `## Task N` section; `implementer-prompt.md` carries no plan-file path; SDD states outright *"Never make a subagent read the whole plan file."* These are the issue's confirmed facts, treated as given.
- The fix therefore lives in **dev-flow's own Stage 2**: the constraints dev-flow imposes on the plan the `writing-plans` subagent produces. Nothing about `task-brief` or the implementer template changes — they are out of scope and out of reach.

## The measurement, re-derived

The issue reports the gh-32-33 plan's Task 2 brief carries "8 `§V` references and 0 occurrences of the plan path." Per this repo's *Measurements are derived* rule I re-derived it rather than copy it. `task-brief`'s `awk` is external (absent, above), so I emulate its documented behaviour — "the text between `## Task N` and the next task heading":

```sh
cd /Users/taylor/dev/claude-plugins
PLAN='docs/superpowers/plans/2026-08-02-gh-32-33-claude-md-conventions-plan.md'
awk '/^## Task 2/{f=1;next} /^## Task [0-9]/{if(f)exit} f' "$PLAN" > /tmp/task2-brief.txt
grep -oE '§V[0-9]+' /tmp/task2-brief.txt | wc -l                                   # printed 9
grep -oE '§V[0-9]+' /tmp/task2-brief.txt | sort -u | tr '\n' ' '                   # printed: §V1 §V2 §V5
grep -c '/docs/superpowers/plans/2026-08-02-gh-32-33-.*-plan.md' /tmp/task2-brief.txt   # printed 0
```

My emulation printed **9** `§V` references (IDs `§V1`, `§V2`, `§V5`) and **0** occurrences of the plan path in Task 2's brief. The count is 9, not the issue's 8; the one-reference gap is a boundary detail of the exact `awk` in the external `task-brief`, which is not in this repo to run — my emulation stops at the next `## Task` heading, and the real script may include or exclude one preamble line differently. The gap does not touch the load-bearing conclusion, which both counts share: **the brief carries multiple unresolvable `§V` IDs and zero copies of the path from which they could be resolved.**

The instruction that tells an implementer how to resolve a `§V` ID lives, in the gh-32-33 plan, only in its `## Global Constraints` (line 26) and in its `## Verification scripts` section preamble (line 73). `task-brief` strips both — they sit before `## Task 1` and inside a non-task section respectively. The concrete failure: Task 2's Step 6 is the **green** run of `§V2`, the `CLAUDE.md`-mandated design-conformance check. An implementer is told *"Run §V2 ... verbatim"* with nothing from which to resolve `§V2`. The failure mode is not a wrong edit that a diff would catch; it is a **silently substituted, weaker verifier** — the implementer invents some plausible check, it passes, and nothing downstream notices.

## The tension this design must resolve, not paper over

The issue *proposes* "carry the plan's absolute path in `## Global Constraints`." The issue's own measurement **disproves that home**: the gh-32-33 plan already put the path plus resolution instruction in `## Global Constraints` (its line 26), and Task 2's generated brief still contained **0** occurrences of the path — because `task-brief` extracts only the `## Task N` section, and Global Constraints sits before Task 1. A fix that lands only in Global Constraints is invisible to the implementer by construction.

The pattern that **worked** is gh-28-29's (plan lines 432, 438): it put the absolute plan path plus a read-verbatim-from-the-plan-file instruction **inside the referencing task step** — which is exactly the span `task-brief` delivers. The rule below places the requirement there, and states explicitly why "Global Constraints only" is insufficient, so a future reader need not re-derive it.

## Approaches considered

**(a) Require the resolver inside each referencing `## Task N` section — chosen.** This is the gh-28-29 pattern. It puts the absolute plan path and the read-verbatim clause exactly where `task-brief` copies them into the brief, so the implementer receives a self-sufficient section. It composes with the better half of gh-32-33's answer — factoring shared verification blocks into a `## Verification scripts` section with `§V` IDs (a real improvement over #24's 20-copy problem) — because the *referencing* task section still names the plan path and instructs the reader to open the shared block from the plan file. Self-sufficiency is a property of each task section, independent of where the shared material is defined.

**(b) Require the resolver in `## Global Constraints` — rejected.** This is the issue's literal proposal and the gh-32-33 plan's actual (failed) choice. `task-brief` strips everything outside `## Task N`; the measurement above shows 0 path occurrences reach the brief. Provably invisible. Rejected on evidence, not taste.

**(c) Teach dev-flow to inject the plan path when it dispatches implementers — rejected as the primary fix.** dev-flow is SDD's controller (Stage 3) and spawns the implementer leaves itself, so it *could* prepend the absolute plan path to every brief. But: (1) SDD's briefs are built by the external `scripts/task-brief` + `implementer-prompt.md`, which this change cannot edit; overriding at dispatch time is a runtime patch living far from where plans are authored, at the wrong stage. (2) It contradicts SDD's deliberate context-hygiene design (*"Never make a subagent read the whole plan file"*) — handing every implementer the whole plan is the thing SDD refuses. (3) It does not actually resolve vague references: a path alone does not tell the implementer that "the table above" is a table 200 lines up, or which `§V` block a step means. Approach (a) forces the plan to name the exact block *and* its path at the point of use, which is self-describing. Injection papers over unresolvable references; authoring self-sufficient sections removes them. Noted here so the rejection is on the record, not rediscovered. Adopting (c) *in addition* to (a), as a fallback, fails the same test: an injected path still cannot tell the implementer that a bare `§V2` must be read rather than invented (reason 3 above), and it would have dev-flow override the external SDD/`task-brief` briefing that deliberately withholds the plan file — a fourth, speculative layer fighting an inherited seam's design, for the case where the Stage 2 rule, its self-review, and the (sharpened) plan-mode reviewer all miss at once. Skipped as over-build.

## Placement decision

**SKILL.md, not CLAUDE.md.** The repo convention (memory, and CLAUDE.md's own division) is: contributor/maintenance rules that a human reads at edit time go in the auto-loaded `CLAUDE.md`; rules the pipeline *applies at run time* belong in `SKILL.md`, which ships into the pipeline's model invocations. This rule governs plan **generation during a dev-flow run** — it shapes what the `writing-plans` subagent produces and what the plan self-review checks — so it is the latter. It goes in `SKILL.md`. Stated here so a reviewer need not rediscover the placement principle.

**A new Stage 2 bullet, folded into the `writing-plans` dispatch and doubling as a plan self-review criterion.** The rule is one production constraint dev-flow imposes on the plan; a dedicated Stage 2 bullet, immediately after the `writing-plans` dispatch bullet, is where dev-flow controls the plan's shape. It is *not* added to the inherited-skills preamble — that preamble governs user-facing decision points, and this is a production constraint, not a user question. It is *not* a separate self-review section — self-review is one clause of the same bullet, because the requirement and its check are the same sentence ("each task section must be self-sufficient; the `writing-plans` subagent halts and reports any it cannot make so").

**Both mirrored pipeline `SKILL.md` files, identical text.** The Stage 2 block exists near-identically in `plugins/dev-flow/skills/dev-flow/SKILL.md` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`; this pair is hand-mirrored (not machine-checked by `scripts/check-sync.py`). The two files' pre-existing Stage 2 differences are only the plugin-qualified review-skill name and the `(worktree as \`working-dir\`)` parenthetical — neither of which this rule touches. So the inserted bullet is **byte-identical** in both files, inserted after the byte-identical anchor line — its byte-identity shown by the `diff` under *The rule* below, and re-proven mechanically at implementation by *Verification* Steps 1–2.

**`dev-flow:adversarial-review` plan mode — sharpen the existing check, add no bespoke one.** The move that stays declined is a *new*, rule-duplicating plan-mode check: copying the Stage 2 self-sufficiency requirement into `adversarial-review`'s `SKILL.md` would put the same rule in two files `check-sync.py` does **not** cross-check against each other (the Stage 2 bullet lives in the pipeline `SKILL.md`, a review check in the review `SKILL.md`), inviting drift for marginal gain — over-build, declined. But the plan cannot lean on the plan-mode reviewer as a backstop *without making it real*. The reviewer already carries a plan-specific check — *"whether each task is executable by a fresh context-free subagent"* — yet the seed reviewer is told nothing about the brief boundary and reads the **whole** plan itself, so it sees `§V2` defined in `## Verification scripts`, judges it resolvable, and does **not** flag the exact defect this design targets. As written the backstop does not fire. The fix is not a new check but a **one-line sharpening of the existing one**: state, in the plan-mode correctness-seed cell, *what the fresh context-free subagent actually receives* — only that task's `## Task N` section, no plan-file path — so the reviewer judges each task from its own section's text, not the whole plan it can see. This supplies the execution **fact** the reviewer's existing check needs; it duplicates no rule (nothing to drift from the Stage 2 bullet), and it lands in the `adversarial-review` `SKILL.md` pair that `check-sync.py` **does** keep byte-identical, so "two copies to sync" is mechanical here, not a manual cost. With it, the three defenses are layered rather than correlated: `writing-plans` authors the sections self-sufficient (Stage 2 dispatch), self-reviews them (the bullet's self-review clause), and an **independent** reviewer that models the executor's real input catches a slip — the independence mattering precisely because the failure is silent (a substituted, weaker verifier that passes).

## The rule — exact SKILL.md text

Insert the single bullet below (block 0) as a **new bullet directly after** this anchor line, which is byte-identical in both files (`plugins/dev-flow/skills/dev-flow/SKILL.md`, `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`). The insertion is anchored on the content of the line below, not on a line number:

```text
- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec).
```

Its byte-identity across the two files is shown by:

```sh
diff \
  <(grep -F 'Spawn a subagent to run `superpowers:writing-plans` against the design' plugins/dev-flow/skills/dev-flow/SKILL.md) \
  <(grep -F 'Spawn a subagent to run `superpowers:writing-plans` against the design' plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md)
# no output, exit 0 -> the anchor line is the same string in both files
```

This design gives its two edits as the design's **only two plain (untagged) fenced blocks** — every other fence here is tagged (`sh`, `text`). **Block 0**, below, is the rule bullet; it names neither the review skill nor the worktree, so it is inserted verbatim into both pipeline files after the anchor above. Shape: `[1, 1]` (each block is one line); block 0 is one source of truth applied to both pipeline files, which mirrors the very DRY discipline this rule teaches.

```
- **Make each `## Task N` section self-sufficient — instruct `writing-plans` so.** SDD briefs one task at a time: `scripts/task-brief` hands the implementer only the text between `## Task N` and the next task heading, with no plan-file path — so anything a task step leans on from **outside that span** (e.g. a shared verification block, an explicit `§`/`§V` ID, another task's output, or an implicit "the table above" / "as defined earlier") is unresolvable from the brief; what triggers the rule is **structural** — the target is not defined within this `## Task N`→next-task span — not how casually the reference reads. The dispatch requires every such cross-section reference to be **either inlined into the task section, or named there by the plan's absolute path** with this clause: *read the referenced block verbatim from the plan file at `<abs-path>`; never reconstruct or substitute it; if you cannot read the plan file, stop and report.* Putting the pointer anywhere `task-brief` strips — `## Global Constraints`, a `## Verification scripts` preamble, **any** non-`## Task N` section — never reaches the implementer, so stating it once outside the referencing task is insufficient by construction. This doubles as the `writing-plans` subagent's own plan self-review criterion: make each section self-sufficient, and **halt and report** any out-of-section reference that cannot be given an in-section pointer rather than ship the plan — the failure is silent, the implementer running a substituted, weaker check for the ID it cannot resolve while nothing downstream catches it.
```

### Companion: the plan-mode reviewer sharpening (block 1)

**Block 1**, below, is the design's second plain fenced block. It **replaces** the existing plan-mode correctness-seed row (the single line beginning `| **plan** |`) in both `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`. That pair is machine-checked line-for-line by `scripts/check-sync.py` (canonicalizing `dev-flow-worktree` -> `dev-flow`); block 1 names neither plugin, so canonicalization is a no-op and both copies are byte-identical. The replacement adds the `task-brief` boundary **fact** to the reviewer's existing *"executable by a fresh context-free subagent"* check; it keeps every other plan-specific check the row already carried, moving that item to the end so its longer clause does not interrupt the list (item order is not semantic).

```
| **plan** | The rubric applied to the plan's approach *and* to any embedded code sketches. | The prose checklist above, plus plan-specific checks: task ordering/dependencies, per-task verification steps, drift from the design doc, and whether each task is executable by a fresh context-free subagent — one that **receives only that task's `## Task N` section (the text up to the next task heading), with no plan-file path**, so judge each task from its own section's text, not the whole plan you can see: a reference to anything outside the section (a shared verification block, a `§`/`§V` ID, "the table above") is unresolvable, and a finding, unless the section inlines it or names it by the plan's absolute path. |
```

## Assumptions (defensible defaults)

- **Block 0's insertion point is after the `writing-plans` dispatch bullet, before the `adversarial-review` bullet.** The rule constrains what `writing-plans` produces, so it reads naturally right after that dispatch and before the review that follows. No blocking ambiguity.
- **Block 1 replaces the existing plan-mode row, identified by content** (the unique line starting `| **plan** |`), not by line number. The prior checks it carried are preserved.
- **The clause names `<abs-path>` as a placeholder, not a literal.** The plan author substitutes the run's absolute plan path (as the gh-28-29 and gh-32-33 plans did). The rule does not hardcode a path.
- **"Self-sufficient" is scoped to the `## Task N` body as `task-brief` delimits it** — text between `## Task N` and the next `## Task` heading. The rule names this explicitly rather than assuming the reader knows `task-brief`'s extent.
- **Shared-verification-block factoring (gh-32-33's `## Verification scripts` + `§V` IDs) remains encouraged, not forbidden.** The rule regulates the *referencing* section, not where shared material is defined; the two compose. No halt is added for defining a shared section.

## Out of scope

- Editing any external superpowers artifact — `writing-plans`, `subagent-driven-development`, `scripts/task-brief`, `implementer-prompt.md`. Not in this repo; cannot be changed here.
- Changing `task-brief`'s extraction behaviour. The rule adapts the plan to what `task-brief` delivers; it does not ask `task-brief` to deliver more.
- Adding a **bespoke, rule-duplicating** `adversarial-review` plan-mode check (declined above). Sharpening the *existing* plan-mode reviewer row with the `task-brief` boundary fact is **in** scope (Placement decision).
- Any change to `CLAUDE.md` — this is a run-time pipeline rule, so it lives in `SKILL.md` (placement decision above).

## Version bump (implementation concern)

All four changed `SKILL.md` files — the two pipeline files and the two `adversarial-review` files — live inside the `dev-flow` and `dev-flow-worktree` plugin directories, so **both `plugin.json` versions bump the minor segment, past `origin/main`** (CLAUDE.md's bump rule; the install cache is version-keyed). No third plugin is touched. Confirmed current == origin/main: `dev-flow` `2.13.0`, `dev-flow-worktree` `1.15.0` (`git show origin/main:plugins/<p>/.claude-plugin/plugin.json | grep '"version"'`). Targets: `dev-flow` -> `2.14.0`, `dev-flow-worktree` -> `1.16.0` (re-confirm against `origin/main` at implementation time; a concurrent branch may have published these numbers first — `python3 scripts/check-version-bump.py origin/main` is the gate).

## Verification (this repo has no test suite — these criteria are the correctness surface)

All mechanical and derived. Run from the repo root on the feature branch.

1. **Both design blocks landed verbatim in their targets — the `CLAUDE.md`-mandated design-sourced check.** This design gives its two edits as two plain fenced blocks (shape `[1, 1]`), so the check re-reads them from the design on disk — never retyped — through `scripts/design_blocks.py` and asserts each lands where intended. `read_blocks(DESIGN, [1, 1])` is itself the shape guard: it exits non-zero if the design's plain-block shape ever moves off `[1, 1]`. `read_blocks` returns a list of blocks, each a list of lines, so block *k*'s single line is `read_blocks(...)[k][0]` (**not** `[k]`, which is the one-element list). Block 0 must be the line **immediately after** the anchor in each pipeline `SKILL.md`; block 1 must be the **unique** `| **plan** |` row in each `adversarial-review/SKILL.md` (uniqueness + equality proves the old row is gone — the removed-phrase check CLAUDE.md's *Always* rule requires). Shape smoke-test first, then the check:

   ```sh
   python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md   # expect: shape: [1, 1]
   ```

   ```sh
   python3 - <<'PY'
   import sys
   from pathlib import Path
   sys.path.insert(0, "scripts")
   from design_blocks import read_blocks
   DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
   b0, b1 = (b[0] for b in read_blocks(DESIGN, [1, 1]))   # [1,1] guards the shape; each block is one line
   ANCHOR = "- Spawn a subagent to run `superpowers:writing-plans` against the design, producing `docs/superpowers/plans/YYYY-MM-DD-<slug>-plan.md` (front-matter links the spec)."
   PIPELINE = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
               "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]
   REVIEW = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
             "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
   bad = []
   for f in PIPELINE:                                    # block 0: line immediately after the anchor
       lines = Path(f).read_text(encoding="utf-8").split("\n")
       at = [i for i, l in enumerate(lines) if l == ANCHOR]
       if len(at) != 1:
           bad.append("%s: anchor found %d times, want 1" % (f, len(at))); continue
       nxt = lines[at[0] + 1] if at[0] + 1 < len(lines) else "<EOF>"
       if nxt != b0:
           bad.append("%s: line after anchor != rule bullet\n    want %r\n    got  %r" % (f, b0[:60], nxt[:60]))
   for f in REVIEW:                                      # block 1: the unique plan-mode row
       lines = Path(f).read_text(encoding="utf-8").split("\n")
       rows = [i for i, l in enumerate(lines) if l.startswith("| **plan** |")]
       if len(rows) != 1:
           bad.append("%s: '| **plan** |' row found %d times, want 1" % (f, len(rows))); continue
       if lines[rows[0]] != b1:
           bad.append("%s: plan-mode row != design block 1\n    want %r\n    got  %r" % (f, b1[:60], lines[rows[0]][:60]))
   for why in bad:
       print("MISMATCH:", why)
   print("design-conformance:", "FAIL" if bad else "OK")
   sys.exit(1 if bad else 0)
   PY
   echo "exit=$?"
   ```

   Expect `design-conformance: OK` and `exit=0`. Run against the base tree, before the edits, it prints four `MISMATCH:` lines and `exit=1` — its demonstrated red form.

2. **Nothing else changed — every touched file is its merge-base blob plus exactly the intended edit.** This is CLAUDE.md's *Always* rule, the one check that proves no *other* line moved (design-conformance in step 1 proves the intended lines are right; this proves nothing else landed, closing the doubled-hunk blind spot that byte-identity-between-copies alone cannot). Per *Command discipline* the merge base is computed in `python3`/`subprocess` and passed to `git` as an `argv` element — never an inline `$(git …)`, which word-splits an empty ref into a different valid command. The removed base plan-row is read from the merge-base blob, not retyped. Expected hunk per file: pipeline `SKILL.md` — block 0 added, nothing removed; `adversarial-review/SKILL.md` — block 1 added, the base `| **plan** |` row removed; each `plugin.json` — exactly one line changed, containing `"version"`. The changed set (excluding this run's own `docs/superpowers/` artifacts, which `docs: commit` commits) must equal exactly these six files.

   ```sh
   python3 - <<'PY'
   import subprocess, sys
   sys.path.insert(0, "scripts")
   from design_blocks import read_blocks   # only to fetch the two blocks from the design
   DESIGN = "docs/superpowers/specs/2026-08-03-gh-45-plan-cross-task-refs-design.md"
   b0, b1 = (b[0] for b in read_blocks(DESIGN, [1, 1]))
   PIPELINE = ["plugins/dev-flow/skills/dev-flow/SKILL.md",
               "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"]
   REVIEW = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
             "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
   PLUGINJSON = ["plugins/dev-flow/.claude-plugin/plugin.json",
                 "plugins/dev-flow-worktree/.claude-plugin/plugin.json"]
   WANT = sorted(PIPELINE + REVIEW + PLUGINJSON)
   def git(*args):
       r = subprocess.run(("git",) + args, capture_output=True, text=True)
       if r.returncode != 0:
           raise SystemExit("FAILED: git %s -- exit %d, %s"
                            % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
       return r.stdout
   base = git("merge-base", "origin/main", "HEAD").strip()
   if not base:
       raise SystemExit("empty merge-base -- refusing to run a HEAD-relative scope check")
   changed = sorted(p for p in git("diff", "--name-only", base, "--", ".", ":!docs/superpowers/").split("\n") if p)
   fail = []
   if changed != WANT:
       for p in sorted(set(changed) - set(WANT)): fail.append("unexpected file: " + p)
       for p in sorted(set(WANT) - set(changed)): fail.append("missing file:   " + p)
   def hunk(f):                                          # added/removed content lines vs merge-base
       out = git("diff", "--no-renames", base, "--", f).split("\n")
       add = [l[1:] for l in out if l.startswith("+") and not l.startswith("+++")]
       rem = [l[1:] for l in out if l.startswith("-") and not l.startswith("---")]
       return add, rem
   def baseline_plan_row(f):
       for l in git("show", "%s:%s" % (base, f)).split("\n"):
           if l.startswith("| **plan** |"): return l
       raise SystemExit("%s: no '| **plan** |' row at merge-base" % f)
   for f in PIPELINE:
       add, rem = hunk(f)
       if add != [b0] or rem != []:
           fail.append("%s: hunk != (add block0, remove nothing); add=%r rem=%r" % (f, add, rem))
   for f in REVIEW:
       add, rem = hunk(f)
       if add != [b1] or rem != [baseline_plan_row(f)]:
           fail.append("%s: hunk != (add block1, remove base plan-row); add=%r rem=%r" % (f, add, rem))
   for f in PLUGINJSON:
       add, rem = hunk(f)
       if not (len(add) == 1 and len(rem) == 1 and '"version"' in add[0] and '"version"' in rem[0]):
           fail.append("%s: expected exactly one \"version\" line changed; add=%r rem=%r" % (f, add, rem))
   for why in fail:
       print("SCOPE FAIL:", why)
   print("file scope + hunks:", "FAIL" if fail else "OK")
   sys.exit(1 if fail else 0)
   PY
   echo "exit=$?"
   ```

   Expect `file scope + hunks: OK` and `exit=0`. A stray edit to any other file, an extra line in any touched file, or a mistyped block fails and is named.

3. **The `adversarial-review` pair stays line-for-line identical, and the boundary fact is present.** Block 1 is byte-identical in both review files, but CLAUDE.md's rule is that machine-checking a pair proves agreement, never correctness — step 1's design-conformance is the outside-the-pair correctness check; this is the agreement check plus a presence grep for the load-bearing phrase:

   ```sh
   python3 scripts/check-sync.py   # expect: pass (adversarial-review pair still line-for-line identical after canonicalization)
   git grep -c 'with no plan-file path' -- \
     plugins/dev-flow/skills/adversarial-review/SKILL.md \
     plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md
   # expect: :1 for each file
   ```

4. **Both plugin versions bumped past origin/main.**

   ```sh
   python3 scripts/check-version-bump.py origin/main   # expect: pass (both touched plugins ahead of origin/main)
   ```

5. **`claude plugin validate .`** exits 0 with exactly the 8 expected missing-author warnings (a PASS, not a regression).

## Spec self-review

- **Placeholders:** `<abs-path>` in block 0 is a deliberate placeholder the plan author substitutes; `<p>` / `<merge-base>` in verification prose are documented as such. No accidental TODO/`<...>` placeholders remain.
- **Consistency:** the chosen home (in-section resolver) is applied uniformly — problem, tension, approaches, rule text, and verification all point at the same seam. The rejected homes (Global Constraints; dispatch injection) are named once and not reintroduced. The plan-mode reviewer sharpening (block 1) is the *independent* backstop the Placement decision argues for, and every downstream section (Summary, Out of scope, Version bump, Verification) accounts for the second edit site and the two extra touched files.
- **Scope:** exactly four `SKILL.md` edits (block 0 into two pipeline files, block 1 replacing the plan-mode row in two review files) + two version bumps. No external artifact, no `task-brief`, no `CLAUDE.md`, no *new* `adversarial-review` check. The idea is one rule plus its independent backstop, in two mirrored pairs — it does not span independent subsystems, so no decomposition/HALT is warranted.
- **Ambiguity:** the one genuine tension (issue's proposed Global-Constraints home vs. the measurement disproving it) is resolved explicitly with evidence; no blocking ambiguity remains, so no HALT.
- **Measurements are derived:** every number this design states was printed by a shown command. `9` `§V` references and `0` plan-path occurrences in the gh-32-33 Task 2 brief — from the `awk`/`grep` block under *The measurement, re-derived* (with the 9-vs-8 discrepancy explained and attributed to the external `task-brief`'s exact boundary). Versions `2.13.0`/`1.15.0` — from the `git show origin/main:…` command under *Version bump*. The anchor's byte-identity across the two pipeline files — from the `diff` under *The rule*, re-proven mechanically at implementation by *Verification* Steps 1–2; the anchor's raw line numbers are deliberately **not** stated as facts, since the insertion is content-anchored. Expected shape `[1, 1]` is asserted about this design's *own* replacement text (two plain-block line counts), so it is stated as a success criterion in *Verification* step 1, not as a claim about the tree. No number appears without its command.
