---
dev-flow:
  slug: gh-63-fully-checked-row
  stops: [pre-merge]
  docs: commit
---

## Original problem

Issue **#63** — "dev-flow resume table: "Plan fully checked" row still carries the pre-#58 raw-count wording"
URL: https://github.com/tayl0r/claude-plugins/issues/63

Full thread (body verbatim; the issue has no comments):

```text
## What

PR #62 (closes #58) re-anchored dev-flow's Execution-complete predicate to `^[[:space:]]*[-*+] \[ \]` in two sites per pipeline SKILL.md: the **Execution-complete signal** paragraph and the Execute resume row ("≥1 unchecked task box …"). It did **not** touch the sibling resume row directly below it:

| … | … |
| Plan at tip has ≥1 unchecked task box (a line matching `^[[:space:]]*[-*+] \[ \]`) | Execute … |   ← anchored by #62
| Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |          ← still says "fully checked"

"Plan fully checked" is the same completion predicate expressed in different words: fully checked ⇔ zero unchecked task boxes. It carries the exact raw-count reading #58 removed — a genuinely-complete plan that still carries `writing-plans`' boilerplate `- [ ]` (blockquote header / inline code span) looks "not fully checked" to a raw `grep -c -- '- [ ]'`.

## Why this wasn't caught in #58

The #58 design scoped its edit via `git grep -nE 'Execution is complete|≥1 unchecked'` and concluded "No other site in either file references the count predicate." That phrase-grep structurally cannot match "Plan fully checked," so the claim is too strong. This row is a measurement blind spot, not a deliberate exclusion.

## Why it is not urgent (no live bug today)

The resume table is "top-to-bottom, first match wins." The "fully checked" row is reached only when the anchored Execute row above it is **false** — i.e. the anchored count is already proven zero. So "fully checked" is correct-by-ordering in practice. This is a robustness/clarity gap (a convention-held invariant that should be construction-held), not the always-fires unsatisfiability #58 fixed.

## The fix (dedicated change)

Reword the "fully checked" row in BOTH mirrored files so it names the anchored predicate, mirroring the Execute row's own parenthetical. Suggested (re-verify at execute time):

    | Plan fully checked — no unchecked task box (no line matching `^[[:space:]]*[-*+] \[ \]`); no PR for the branch (`--state all` list empty) | PR: create + review |

Files (hand-mirrored pair; `check-sync.py` does NOT cover it — edit both and cross-verify the new string is byte-identical in each):
- `plugins/dev-flow/skills/dev-flow/SKILL.md` (the "Plan fully checked" resume row)
- `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (same row)

Also, as part of the same change, correct the #58 design's over-strong "No other site references the count predicate" claim (it missed this row), and bump both plugin `version`s (behavior-adjacent prose change; cache is version-keyed).

## Out of scope

No behavior change is needed to unblock anything — the ordering keeps routing correct today. This is a wording/robustness fix so the partition is explicit and survives a future row reorder or an independent (non-ordered) reading.

_Surfaced by dev-flow's diff-stage adversarial review of #62._
```

# gh-63: name the anchored predicate in the "Plan fully checked" resume row

**Ruling: SHIPS**, as a one-row whole-line replacement in each pipeline `SKILL.md` (the hand-mirrored pair), the amendment of one over-strong claim in the gh-58 design doc, and a version-bump pair. The "Plan fully checked" resume row is reworded to name the anchored count predicate — `no line matching \`^[[:space:]]*[-*+] \[ \]\`` — as the exact negation of the anchored Execute row's predicate directly above it, so the partition "≥1 unchecked box" / "fully checked" is explicit and no longer depends on the table's "first match wins" ordering to be read correctly. The gh-58 design's "No other site in either file references the count predicate" claim is amended: it was a measurement blind spot, because the phrase-grep `Execution is complete|≥1 unchecked` structurally cannot match "Plan fully checked". No behavior changes; the reword makes the partition explicit in the prose rather than construction-held — routing remains correct-by-ordering, an invariant the ordering already upholds.

## What was verified before designing

Base captured once and reused: `base=$(git merge-base origin/main HEAD)` (validated non-empty) — the merge-base, per the repo's `## Verifying a change` byte-for-byte contract. On this branch `HEAD == origin/main == 76a93909da5cc802ad1ed393d5f9620cb823730d`, so the merge-base is that same SHA and every number below, measured at `$base`, describes the pre-edit tree. Each claim gives the command that printed it, in the past tense at `$base`.

- **The current row, byte-identical in both files.** `git show "$base:plugins/dev-flow/skills/dev-flow/SKILL.md" | sed -n '196p'` and the worktree `:190` produced identical bytes:
  ```text
  | Plan fully checked; no PR for the branch (`--state all` list empty) | PR: create + review |
  ```
  It sits directly below the anchored Execute row at `:195` / `:189` respectively, which is identical in both files:
  ```text
  | Plan at tip has ≥1 unchecked task box (a line matching `^[[:space:]]*[-*+] \[ \]`) | Execute — resume at first unchecked task (cross-check ledger + `git log`) |
  ```
- **The removed phrase appears only at those two rows.** `git grep -F -- 'fully checked;' -- plugins/` returned exactly two lines (`dev-flow:196`, `worktree:190`). After the edit it must return none.
- **The anchored-predicate literal appears on four lines at `$base`.** `git grep -F -- '^[[:space:]]*[-*+] \[ \]' -- plugins/` returned `dev-flow:169` and `:195`, `worktree:163` and `:189` — the Execution-complete paragraph and the Execute row in each file. After the edit it must appear on six (the new rows included).
- **The proposed wording is absent from the shipped files at `$base`.** `grep -rnE 'no unchecked task box|no line matching' plugins/` returned nothing, so the design-conformance assertion below cannot false-pass before the edit. Scoped to `plugins/`, and `-E` rather than BRE `\|` (a literal on BSD grep, an alternation on GNU/ugrep), because dated `docs/` records legitimately carry the phrase — the tracked gh-48 plan and this design's own `## Original problem` both quote "no unchecked task box" — per the same dated-record reasoning the removed-phrase grep below applies.
- **The gh-58 claim is a single site.** `grep -rn 'No other site' docs/ plugins/` returned exactly one hit: `docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md:31`, inside the bullet beginning `**The two target sites, per file.**`. The gh-58 design does not otherwise mention "Plan fully checked" (`grep -n 'Plan fully checked\|fully checked'` returned nothing there), so the amendment is one line in one file.
- **Version state.** `git show "$base:plugins/<name>/.claude-plugin/plugin.json"` gives `dev-flow` **2.19.0** and `dev-flow-worktree` **1.21.0**; the working tree matches, and `origin/main` is at the same two versions — so bumping the minor segment past `origin/main` (2.20.0 / 1.22.0) clears `scripts/check-version-bump.py`.
- **The checkers' baseline.** `python3 scripts/check-sync.py` exited 0 at `$base`; `python3 scripts/check-version-bump.py origin/main` exited 0 ("no plugin directory touched") at `$base`; `claude plugin validate .` exited 0 with the 8 expected "No author information provided" warnings.

## The fix — exact replacement text

Two whole-line replacements plus one sentence amendment. The blocks below are the design's only plain (untagged) fenced blocks, in document order — **shape `[1, 1]`** for `scripts/design_blocks.py` (the `text`-tagged fences elsewhere are excluded from the shape).

**Block [0] — the new "Plan fully checked" resume row; replaces the current row in BOTH files (byte-identical in each):**

```
| Plan fully checked — no unchecked task box (no line matching `^[[:space:]]*[-*+] \[ \]`); no PR for the branch (`--state all` list empty) | PR: create + review |
```

The trigger cell negates the Execute row's predicate: "no unchecked task box" mirrors "≥1 unchecked task box", and the parenthetical `(no line matching \`^[[:space:]]*[-*+] \[ \]\`)` is the literal negation of that row's `(a line matching \`^[[:space:]]*[-*+] \[ \]\`)`. The cell as a whole is not the exact complement of the Execute cell: it adds the no-PR conjunct and opens with a different frame ("Plan fully checked —" vs "Plan at tip has …"), and a plan with zero unchecked boxes but an existing PR satisfies neither cell, falling through to the PR-review rows — so the partition is closed by the table's ordering, not by the two cells alone. The second condition ("no PR for the branch (`--state all` list empty)") and the second cell ("PR: create + review") are preserved verbatim. The bytes are the issue's suggested text, extracted from the issue body minus its 4-space markdown code-block indent (a table row cannot be indented); after that strip the bytes match the issue verbatim (repr-verified: one em dash U+2014; the only asterisks are inside the regex code span).

**Block [1] — the amended line 31 of the gh-58 design doc (the corrected sentence is embedded in the bullet):**

```
- **The two target sites, per file.** `git grep -nE 'Execution is complete|≥1 unchecked' -- plugins/` returned exactly two lines in each file: the **Execution-complete signal** paragraph and the resume-table row. `plugins/dev-flow/skills/dev-flow/SKILL.md:165` / `:191`; `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:159` / `:185`. No other site in either file references the count predicate — **a claim corrected by gh-63**: the sibling "Plan fully checked" resume row directly below the anchored Execute row also expresses the count predicate, in different words that the phrase-grep `Execution is complete|≥1 unchecked` structurally cannot match, so this claim was a measurement blind spot, now fixed. The Stage 3 **Bookkeeping** bullet (`:231` / `:225`) mentions *ticking* (the action) but no count, so it is untouched.
```

The single amendment: `references the count predicate.` → `references the count predicate — **a claim corrected by gh-63**: the sibling "Plan fully checked" resume row directly below the anchored Execute row also expresses the count predicate, in different words that the phrase-grep `Execution is complete|≥1 unchecked` structurally cannot match, so this claim was a measurement blind spot, now fixed.` The correction marker is bolded so the record's default reading is the correction, not the claim. The line's file citations are **not** refreshed: this is a dated record whose numbers are measurements at `$base` (per its own framing), so they stay at their gh-58-era values (`:165`/`:191`, `:159`/`:185`, `:231`/`:225`) — refreshing one line's citations would mix a live-pointer reading into a snapshot record and contradict the sibling citations that remain at their gh-58-era values. Every other byte of the line is unchanged; the original claim's wording survives as the prefix of the amended sentence, so the correction reads as an amendment, not a rewrite of the record.

## Version bumps

Both plugin directories are touched (each carries an edited `SKILL.md`), so `scripts/check-version-bump.py` requires a bump ahead of `origin/main`'s tip for each. Bump the **minor** segment, past `origin/main` (not merely past this branch's base):

- `plugins/dev-flow/.claude-plugin/plugin.json`: `2.19.0` → **`2.20.0`**
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`: `1.21.0` → **`1.22.0`**

(Re-check both against `origin/main` at execute time; if `origin/main` has advanced past these numbers, bump past whatever it then publishes.)

## Mirrored-pair obligation

The pipeline `SKILL.md` pair is **hand-mirrored**, not machine-checked — `scripts/check-sync.py`'s `MIRROR_PAIRS` does not include it (verified: it holds only the `adversarial-review` SKILL + agent bodies and manifest `description`s). Therefore **both** files must be edited with the identical string, and the change cross-verified against something **outside** the pair: here that is the design-conformance check (one block asserted verbatim in *both* files — this rules out a two-copies-differ mistake, but not a single mistype propagated to both, which criterion #2's issue-text tie closes as far as an in-repo check can), the fixed-string count, and the issue's commissioned wording (criterion #2).

## Approaches considered

- **In-place reword adopting the issue's suggested text (chosen).** One whole-line replacement per file; the trigger cell names the anchored predicate as its exact negation, mirroring the Execute row's parenthetical.
- **Reword without the "no unchecked task box" restatement** (e.g. `Plan fully checked (no line matching ...)`). Rejected: "no unchecked task box" is not decoration — it is the term the reader already met in the Execute row ("≥1 unchecked task box"), so keeping it makes the two rows read as mirror images of one predicate; a reader can verify the partition at a glance.
- **Tighter syntactic mirror preserving the Execute row's frame** (e.g. "Plan at tip has 0 unchecked task boxes (no line matching `^[[:space:]]*[-*+] \[ \]`); no PR for the branch (`--state all` list empty)") — structurally the closest mirror of the Execute cell, flipping only the quantifier (≥1 → 0) and the parenthetical sign (a → no line). Rejected: it drops the "Plan fully checked" label, the term the row's routing concept and this issue are built on, for a symmetry the reader does not need; the chosen bytes already name the anchored predicate as its exact negation while keeping the object phrase ("unchecked task box") the Execute row introduced — which is what makes the two rows legible as a partition. The no-PR conjunct is orthogonal to the completion partition and belongs to the PR:create routing.
- **Leave the gh-58 claim untouched, noting the correction only in this design.** Rejected: the issue explicitly asks to correct the claim, and it is a live factual claim inside a dated record, not a quote of the old row wording — a known-false statement there perpetuates the blind spot for the next reader. Amending it in place (prefix-preserving) marks it corrected without rewriting the record.
- **Also touch the anchored Execute row or the Execution-complete paragraph.** Rejected as out of scope: both already name the predicate; only the sibling row carried the old wording.
- **Define the anchored predicate once and have the resume rows reference it instead of restating the literal** (a "single canonical definition" seam). Rejected: the resume table is a routing table whose trigger cells must read standalone — the issue's own rationale for this change is that the row must survive "a future row reorder or an independent (non-ordered) reading", and a row that dereferences the Execution-complete paragraph re-couples it to exactly the ordering this change is meant to remove. The sibling Execute row already restates the literal (the #58/#62-validated pattern), so this row completing the mirror image is consistency with the seam, not a third competing definition — the paragraph remains canonical, and criterion #4 pins all three per-file copies to it character-for-character. The standing-drift residual (a future edit to one site's literal not mirrored to the others) is accepted: it fails safe (the table's ordering still routes correctly; the row is documentation), and guarding it would mean a fourth standing checker for one prose string in a repo whose verification is deliberately per-change.

## Assumptions

- **The resume table keeps its "top-to-bottom, first match wins" semantics and the row keeps its position directly below the anchored Execute row.** The edit is a whole-line replacement of an existing row; no row is added, removed, or reordered. This is why the change is non-urgent: the "fully checked" row is only reached when the anchored count is already proven zero.
- **The parenthetical ships byte-identical to the anchored predicate** (the fixed string `^[[:space:]]*[-*+] \[ \]`), so the predicate the row names is character-for-character the one #58/#62 validated. The success criteria pin this.
- **The replacement string is byte-identical across the pair** — one block asserted in both files, never two separately-typed copies.
- **`check-sync.py` stays green with no new entries** — the edit touches no `MIRROR_PAIRS` member and no `description`.
- **The removed-phrase grep is scoped to `plugins/`** — the old row wording legitimately survives in dated records (this design's `## Original problem`, the issue thread), per the gh-58 precedent.

## Success criteria / verification

No test suite exists in this repo; verification is greps, the design-block re-read, and the two checker scripts. Every git ref a criterion computes is captured, validated non-empty, and quoted — never an unguarded inline substitution (Command discipline). Capture once: `base=$(git merge-base origin/main HEAD)` and halt if empty — the blob-reconstruction base is the **merge-base** (the contract's term: a bare `origin/main` would absorb concurrent changes and fail a correct edit spuriously; a hardcoded SHA would strand behind a moved fork point). Version checks separately consult `origin/main`'s tip (criterion 6, plus the Version bumps section's execute-time re-check).

1. **Removed phrasing is gone (the removed-phrase grep).** `git grep -F -- 'fully checked;' -- plugins/` returns no hits (at `$base` it returned exactly the two rows).
2. **New phrasing landed in both files (design-block re-read, never retyped).** A per-change `python3` check that `sys.path.insert(0, "scripts")`, calls `read_blocks("docs/superpowers/specs/2026-08-08-gh-63-fully-checked-row-design.md", [1, 1])` (run `python3 scripts/design_blocks.py <this design>` first to confirm the shape is `[1, 1]`), and asserts: Block [0] appears verbatim in `plugins/dev-flow/skills/dev-flow/SKILL.md` and in `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` (one block → byte-identical across the pair); Block [1] appears verbatim in `docs/superpowers/specs/2026-08-03-gh-58-completion-predicate-design.md`. Additionally assert Block [0]'s single line equals, modulo leading whitespace on both sides, the issue's suggested row inside the design's `## Original problem` fenced block (the unique line there whose stripped form begins `| Plan fully checked —`). `## Original problem` is caller state fetched from the issue, the one independent in-repo copy of the row's bytes, so this closes the single-mistype case as far as an in-repo check can: a prose typo in the block (outside the literal pinned by criterion #4) can no longer propagate identically to both files and pass every criterion. A mistype in the issue fetch itself would land in both copies and pass the tie; that residual is covered by the design-time repr-verification of Block [0] against the live issue (the Block [0] paragraph above), not by this check.
3. **Every touched file is byte-for-byte its merge-base (`$base`) blob with exactly the intended edit.** `verify_blob` (`blob(base, path)`, `to_lines`, `reconstructed`), reading raw bytes: the `dev-flow` `SKILL.md` equals its base blob with line `:196` (the line matching `| Plan fully checked;`) replaced by Block [0]'s line; the worktree `SKILL.md` the same at `:190`; the gh-58 design doc equals its base blob with line `:31` (the line containing `No other site in either file references the count predicate`) replaced by Block [1]'s line; each `plugin.json` equals its base blob with its `"version"` value changed. The design doc itself is a newly created file, so its own `verify_blob` base is empty.
4. **The shipped literal equals the anchored predicate.** After the edit, `git grep -F -- '^[[:space:]]*[-*+] \[ \]' -- plugins/` returns exactly **six** lines (three per file: the Execution-complete paragraph, the Execute row, the new fully-checked row) — up from four at `$base`. The regex in the new row is character-for-character the one the other two sites carry.
5. **`python3 scripts/check-sync.py` still exits 0.** No `MIRROR_PAIRS` member and no `description` is touched.
6. **`python3 scripts/check-version-bump.py origin/main` exits 0.** Both plugins are touched and both are bumped ahead of `origin/main`'s tip (2.20.0, 1.22.0).
7. **`claude plugin validate .` passes** — exits 0 with the same 8 expected "No author information provided" warnings as at `$base`.

## Out of scope

- No change to the anchored Execute row, the Execution-complete signal paragraph, the Stage 3 Bookkeeping bullet, or any other prose in either `SKILL.md`.
- No change to `writing-plans` or any other plugin.
- No retroactive edit of other dated specs/plans that quote the old row wording — only the gh-58 design's live claim sentence is amended, because the issue commissions it and it is a live scope claim (a completeness assertion future readers rely on), not a quote of the old row wording.
- No new tooling and no runtime behavior change: the reword documents an invariant the ordering already upholds.
