---
dev-flow:
  slug: gh-53-computed-base
  stops: [pre-merge]
  docs: commit
---

# gh-53 — a this-change success criterion computes its base; it does not hardcode one

## Problem / Motivation

PR #52 landed a rule inside **Command discipline** (both hand-mirrored pipeline
`SKILL.md`s) saying that a success criterion consuming a **computed** git ref
must pass it to `git` as an `argv` element from `python3`/`subprocess`. That
rule is deliberately silent on *whether* the ref should be computed in the first
place — and that silence is the gap #53 names.

The shipped bullet's scope is "a step that consumes a **computed** git ref". A
criterion that hardcodes its base — `git diff --name-only bf7676b -- …` — is out
of scope by construction, and stays writable as one line of shell. For a
criterion recording a **pre-edit measurement of the tree** that is correct and
intended: a literal SHA is exactly how a measurement reproduces after merge, and
the **Measurements are derived, not typed** bullet already prescribes it (`git
grep … <base> -- …`, past tense, at that revision).

But a **scope / diff / reconstruction** check is the opposite case, and nothing
in the guidance says so. The precedent already exists — it just lives in one
design instead of in the pipeline's own rules. The verification-blocks design's
`## Verification` preamble
(`docs/superpowers/specs/2026-08-02-gh-40-41-verification-blocks-design.md`) is
built on the distinction: *"The base is `git merge-base origin/main HEAD` —
computed, never hardcoded, so it stays correct if `main` advances or the branch
is rebased."* `scripts/verify_blob.py` and `CLAUDE.md`'s **Verifying a change**
section both take their reconstruction base from `git merge-base` for the same
reason. So the *practice* of computing the base is settled and dogfooded; the
only thing missing is that it is unwritten as guidance the pipeline emits.

**The failure mode to name.** A hardcoded base in a this-change check silently
stops meaning "what this branch changed" the moment the branch is rebased or the
default branch advances. It becomes "what changed since some commit" — which on
a rebased branch can fold in other people's work or omit your own — and it fails
in the direction that reads **green** (a scope/reconstruction check that no
longer compares against the true fork point still prints OK). The harness pushes
authors straight at this hazard: a capture and its consumer must share one Bash
call, that compound form is refused ("break it into plain, separate commands"),
and shell state does not persist between calls — so the path of least resistance
is to paste the SHA in as a literal.

## Decision

**Extend the existing `Measurements are derived, not typed` bullet** (option A)
with the this-change pole of the base-choice axis it already draws, cross-linking
the argv mechanics to **Command discipline**. One inserted passage, byte-identical
in both `SKILL.md` copies; no new bullet.

### Why the Measurements bullet is the right home

That bullet already owns the base-choice axis — it just never stated this pole.
It contrasts a claim about the artifact's **own replacement text** (asserted in
its own success criteria, no base) with a measurement of the **tree before the
edit** (pinned to a literal base revision, `git grep … <base> -- …`, past tense).
The pre-edit-measurement pole *is the literal half* of exactly the split #53 is
about. What is missing is the complementary pole: a measurement of **the change
itself** — its file scope, its diff, its byte-for-byte reconstruction — must
*track* the moving fork point, so it **computes** its base
(`git merge-base origin/<default> HEAD`) instead of pinning one. Adding it
completes the axis in the one place that already carries half of it, rather than
opening a second site that would have to restate the pinned-literal half to make
sense.

**Frame fit (addressed honestly).** The bullet is titled *Measurements are
derived, not typed*. A scope / diff / reconstruction check is a measurement taken
against a base ref — `git diff --name-only <base> -- plugins/` is the same shape as
the pre-edit `git grep … <base> -- …` the bullet already governs, and a
reconstruction check is an assertion built on such a measurement (working tree vs.
the base blob). Where it differs from the two existing poles is worth stating
plainly rather than eliding: those poles govern a measurement's *stated output
value* — a number you must derive rather than type — whereas this pole governs the
measurement's *input base ref*. That is not a departure from the title; it is the
same title applied one level in — the base, too, is *derived, not typed*
(`git merge-base …`, never a hardcoded SHA). And the choice of base is the very
axis the pre-edit pole already draws: a measurement of a fixed historical tree pins
a literal base so it reproduces; a measurement of *this change* computes its base
so it tracks the moving fork point. Same axis, complementary pole — the title stays
accurate and no retitle is needed.

**Seam with Command discipline (the upstream/downstream split).** The new rule is
*upstream* of PR #52's argv rule: it says **when** a base must be computed;
Command discipline's argv clause says **how** to pass a computed ref once you
have one ("a step that consumes a **computed** git ref runs its `git` calls
through `python3`/`subprocess` with the ref as an `argv` element"). The inserted
text hands off to it in a parenthetical — *"a computed ref, passed to `git` as an
`argv` element per **Command discipline**"* — so Measurements owns the
compute-vs-pin decision and Command discipline owns the safe-passing mechanics,
each in one place, threaded rather than duplicated.

### Rejected alternatives

- **(B) A new standalone Cross-Cutting bullet for base-ref choice.** Rejected:
  it fractures a single axis across two bullets. The lighter form of B — a
  standalone bullet that *cross-references* the Measurements bullet for the
  pinned-literal (pre-edit) pole instead of restating it — avoids the duplication
  but not the fracture: a reader still has to visit two bullets to see one axis,
  and the new bullet makes sense only by pointing back at the pole Measurements
  already owns. Since Measurements already carries one pole, adding its complement
  there keeps the whole axis in one place — strictly better than a second bullet
  that must reach back into the first. (Restating the pre-edit half rather than
  cross-referencing it would be worse still — the same distinction met twice — but
  the cross-ref form is the fair comparison, and A wins against it too.) Rule
  proliferation for what is one axis with two poles.

- **(C) Complete Command discipline's argv thought at its own site.** Rejected:
  it puts a **when-to-compute** rule inside a **how-to-pass** bullet. Command
  discipline's frame is the empty-producer / word-splitting hazard — how command
  output is captured and passed so an empty value cannot invert a predicate. The
  compute-vs-pin choice is a different axis (which criteria are relative-to-base
  vs. pinned-to-a-literal, keyed on *what the criterion asserts*), and it belongs
  with the pre-edit/own-text split, not with argv safety. Command discipline is
  also already the densest bullet in the section; folding a second distinction in
  over-widens it past its frame. The clean design is the cross-reference in
  option A, not a merge.

## The exact edit

**Both** `SKILL.md` copies carry this bullet **byte-for-byte identically** (the
Measurements bullet has no declared per-copy differences — it names no plugin and
no routing ref), so the replacement below is applied verbatim to both. It is a
**pure insertion** into the existing single-line bullet: two sentences are spliced
in after `… state no number its output does not show.` and before `A spec
self-review names …`. Nothing existing is deleted or reworded.

Targets (located by the unique marker line `Measurements are derived, not typed`,
one per file — not by a fixed line number, so a shifted base fails loudly rather
than editing the wrong line):

- `plugins/dev-flow/skills/dev-flow/SKILL.md` (the Measurements bullet)
- `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (the same bullet)

The full **post-edit** bullet, produced by applying the splice to the file on
disk in `python3` and printing the result (not retyped), given as a plain
fenced block so a plan's design-conformance check can re-read it from this
document:

```
- **Measurements are derived, not typed.** Every measurement an artifact states was printed by a command its author ran, or it is cut. A measurement of the artifact's **own replacement text** — a word or line count, "the shortest bullet", "in seven words" — is asserted in that artifact's own success criteria: the text is still under the author's hand, and a later rewrite silently falsifies anything typed beside it. A measurement of the **tree before the edit** is the opposite case — re-deriving it afterwards falsifies a design that is correct — so give the command pinned to the base revision (`git grep … <base> -- …`) beside the claim, state the claim in the past tense at that revision, and state no number its output does not show. A measurement of **the change itself** — its file scope, its diff, its byte-for-byte reconstruction — is the mirror image of that one: it must keep tracking what *this branch* changed as the base moves, so it computes its base with `git merge-base origin/<default> HEAD` (a computed ref, passed to `git` as an `argv` element per **Command discipline**), never a hardcoded SHA. A hardcoded base there fails in the direction that reads **green** — the moment the branch is rebased or the default branch advances, it silently stops measuring what this branch changed and starts measuring what changed since some commit, folding in others' work or dropping your own. A spec self-review names every measurement the artifact states and the command that printed it.
```

The inserted text only (for reviewer convenience; it is the second and third
sentences added mid-bullet, and is *not* a separate edit — it is the delta
already contained in the block above):

> A measurement of **the change itself** — its file scope, its diff, its byte-for-byte reconstruction — is the mirror image of that one: it must keep tracking what *this branch* changed as the base moves, so it computes its base with `git merge-base origin/<default> HEAD` (a computed ref, passed to `git` as an `argv` element per **Command discipline**), never a hardcoded SHA. A hardcoded base there fails in the direction that reads **green** — the moment the branch is rebased or the default branch advances, it silently stops measuring what this branch changed and starts measuring what changed since some commit, folding in others' work or dropping your own.

Terminology note: `<default>` is the pipeline's already-resolved default branch
(SKILL.md's *Base ref and `<default-ref>`* step). `origin/<default>` spells the
remote prefix explicitly, matching the `origin/<baseRef>` form the Docs-policy
`merge_base` uses and the routing-ref rule's insistence that `origin/` is spelled,
never assumed — while the concrete `origin/main` stays in the repo-specific
verification sections that dogfood the rule.

It is deliberately **not** `<default-ref>` — the fetch-free, staleness-tolerant
abstraction the routing predicates use. Those predicates bound a
`<default-ref>..<branch-ref>` range and tolerate a stale (or local-fallback) base
because their slug-anchored greps discard whatever extra base-side commits it drags
in; a scope / diff / reconstruction check has no such filter, so it must resolve the
*true, current* fork point, and a local-fallback base sitting behind that point
would silently widen the measured scope with others' base-side commits — the exact
green failure this bullet names. So it wants `origin/<default>`, and when that ref
is unresolvable (a never-fetched or remote-less checkout) a loud halt rather than a
fallback: `git merge-base origin/<default> HEAD` then prints nothing and exits
non-zero, which Command discipline's *capture, validate non-empty, a failed producer
halts* rule — already cross-referenced in the bullet — turns into a halt, never a
silent measurement against the wrong base. That is the dogfooded stance: the
verification-blocks design assumes `origin/main` is fetchable and fails loudly,
naming git's message, rather than comparing against a stale ref (its A10).

## Affected files

- `plugins/dev-flow/skills/dev-flow/SKILL.md` — Measurements bullet, insertion above.
- `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` — same bullet, byte-identical insertion.
- `plugins/dev-flow/.claude-plugin/plugin.json` — minor `version` bump, landing strictly past whatever `origin/main` holds at execute time (`python3 scripts/check-version-bump.py origin/main`, criterion 5). No number is fixed here: a concurrent branch may take the next one, and the check reads the baseline at execute time.
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — same: a minor `version` bump past `origin/main`'s at execute time, verified by that same check.
- `docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md` — this design (committed; `docs: commit`).
- `docs/superpowers/plans/2026-08-05-gh-53-computed-base-plan.md` — the plan (committed).

No other files change. `scripts/`, `CLAUDE.md`, `CONTEXT.md`, `.claude-plugin/marketplace.json`, both `README.md`s, `docs/adr/`, and the `adversarial-review` mirrored pair are all out of scope: this is prose guidance added to one bullet, and it names no instrument to relocate (that would be #39's move, not this one).

## Success criteria / Verification

Run from the repo root, after the edit unless stated. The reconstruction base is
**computed, never hardcoded** — `git merge-base origin/main HEAD` — and passed to
`git` as an `argv` element from `python3` (this change dogfooding its own rule).

1. **Replacement landed, verbatim, in both copies.** The plan's design-conformance
   check re-reads the replacement from *this* document rather than retyping it:
   `python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-05-gh-53-computed-base-design.md`
   reports a single plain block of shape `[1]`; the check then
   `sys.path.insert(0, "scripts")`, `read_blocks(<this-design>, [1])`, and asserts
   block `0`'s single line appears verbatim in **both** target files. (If later
   edits to this design add another untagged fenced block, the shape argument the
   plan passes must be updated to match — the reader exits non-zero if it moved.)

2. **Removed-phrase grep (the broken adjacency).** This is a pure insertion, so
   the only text that ceases to exist is the old sentence junction. Assert
   `grep -F "does not show. A spec self-review"` returns **no** hits in either
   `SKILL.md` (the two sentences are no longer adjacent). Expect exit 1 / empty.

3. **Byte-for-byte merge-base blob reconstruction** (CLAUDE.md *Verifying a
   change*, **Always**). For each `SKILL.md`: read raw bytes, locate the bullet by
   its unique `Measurements are derived, not typed` marker line in the merge-base
   blob, splice in the replacement line, and assert the working-tree file is
   byte-for-byte that blob with **exactly** that one line replaced and nothing
   else moved. Use `verify_blob` (`sys.path.insert(0, "scripts")`; `blob(base,
   path)`, `to_lines`, `reconstructed`) so a lost trailing newline or a CRLF flip
   cannot pass. `base = git("merge-base", "origin/main", "HEAD")` via `subprocess`
   argv, validated non-empty before use.

4. **The two copies stay mirrored — by hand.** `scripts/check-sync.py` does **not**
   cover this pipeline `SKILL.md` pair (it covers the `adversarial-review` pair and
   the manifest `description`s only). So verify the mirror directly, comparing the
   bullet's **bytes** and not its line number — it sits at a different line in each
   copy (279 vs 273 today), so any check that prints line numbers reports a spurious
   difference:
   `diff <(grep -F "Measurements are derived, not typed" plugins/dev-flow/skills/dev-flow/SKILL.md) <(grep -F "Measurements are derived, not typed" plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md)`
   must print nothing and exit 0. `grep -F` (fixed string, **no** `-n`) returns each
   file's whole bullet line with no line-number prefix, so byte-identical bullets
   compare equal wherever each sits, and any real divergence exits 1. This relies on
   the bullet being a single line, which the edit preserves (it is a pure insertion
   into the existing single-line bullet); if a later change ever reflows it across
   multiple lines this grep would compare only the marker line, so replace it then
   with a byte-range extract. This is the *outside-the-pair* check CLAUDE.md requires
   for any mirrored-pair edit: criteria 1–3 verify each copy against the design and
   its own merge-base blob, independently of the other copy, so a doubled-but-wrong
   edit cannot pass unseen.

5. **Version bumps past `origin/main`.** Both plugins' `SKILL.md` behavior text
   changes, so each `plugin.json` `version` must move — a **minor bump landing
   strictly past whatever `origin/main` holds at execute time**, not a number fixed
   here, since a concurrent branch may already have published the next one.
   `python3 scripts/check-version-bump.py origin/main` is exactly that check — it
   compares each touched plugin's head version against `origin/main`'s *tip*, not the
   merge base — and must exit 0 for both.

6. **Marketplace still valid.** `claude plugin validate .` exits 0 (author-less
   warning count unchanged; no new plugin, no author key touched).

## Assumptions / open questions

- **Docs policy = `commit`** (front-matter `docs: commit`): the repo commits
  dev-flow design/plan artifacts to `docs/superpowers/{specs,plans}/`, and there is
  no `.claude/dev-flow.local.md`, so the `commit` default applies (CLAUDE.md
  *Workflow*).
- **Both plugins get a minor version bump** because each `SKILL.md`'s behavior text
  changes (CLAUDE.md *Changing a plugin*). Exact numbers are gated on `origin/main`
  at execute time (criterion 5), not fixed here.
- **The inserted text needs no mirror adjustment.** The Measurements bullet is
  byte-identical across the two copies today and the addition introduces no
  plugin-name or routing-ref reference, so both copies receive the same bytes —
  confirmed by splicing both files' current bullet and comparing the results.
- **Placement is a design call, resolved to (A) with reasons above.** The issue
  framed it as open; no user question remains. If a reviewer prefers to *also*
  name the specific criterion families (scope / diff / reconstruction) in Command
  discipline's argv clause, that is a larger rewrite of two bullets and is
  explicitly rejected here as over-widening (option C); it is not left open.
