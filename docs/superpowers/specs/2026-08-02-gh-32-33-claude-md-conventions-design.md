---
dev-flow:
  slug: gh-32-33-claude-md-conventions
  stops: [pre-merge]
  docs: commit
---

# gh-32 / gh-33: write down the two conventions `CLAUDE.md` leaves to judgment

## Goal

Both issues ask the same question about the same file — *which unwritten convention should become a written rule in `CLAUDE.md`?* — and both are answered **yes, with the rule narrowed to the part that is actually invariant**.

- **#32** — mirrored-pair verification proves the intended lines changed, never that no other line did. The **property** ("every file the edit touches is byte-for-byte its merge-base blob with exactly the intended edit applied") joins the `Always:` list on line 9. The **instrument** does not: three consecutive changes each invented a different one, and the check #32 sketches cannot run on an insertion, a deletion, or a created file.
- **#33** — the bump rule says *whether*, not *how much*. Line 7 gains **always the minor segment**, with major reserved for when a plugin is split or renamed.

One file changes: `CLAUDE.md`, lines 7 and 9, each a whole-line replacement. **No `scripts/` change, no plugin file, no version bump.** That is a conclusion, not a deferral — there is no HALT in this design.

A third question surfaced by the evidence — two concurrent branches silently taking the same version number — is ruled a **separate concern**, recorded here in full and filed as its own issue by the pipeline. It is deliberately not smuggled into #33's rule; see *The concurrent-bump collision is a separate concern*.

## Scope check — one subsystem, one file, two lines

One subsystem: this repo's written contributor conventions. Both issues are "an unwritten convention is being re-derived per change; should it be written down?", both answers land in `CLAUDE.md`'s *Changing a plugin* section, and the two edits are independent whole-line replacements on non-adjacent lines with no shared text and no ordering dependency. Shipping them as one change is right: one file, one review, one design-conformance check. Nothing here decomposes further and nothing conflicts.

#33's own scope note — *"#24 also proposes `CLAUDE.md:9` edits — same file, adjacent bullet, so sequence them"* — is already discharged: #24 merged as `963a66c`, and this design is written against the post-#24 line 9, quoted in full in block 1.

## Issue #32 — the property is universal, the instrument is not

### What is true today, measured on `b4b5d1c`

`CLAUDE.md` line 9 names the hazard by name — *"text mangled identically in both sides passes it"* — and then prescribes two checks, neither of which closes it. A reader who follows the bullet exactly is unprotected against the failure the bullet itself describes. That is an internal inconsistency in the document, and it is the whole of #32's case.

What the repo actually does instead. The last three changes each proved "nothing else moved", with a different instrument each time, none of them written down anywhere:

| Change | Shape of the edit | Instrument it invented |
|---|---|---|
| gh-26 (`c8b2182`) | one line replaced in `CONTEXT.md` | `git diff --stat` asserted to ` CONTEXT.md \| 2 +-` and `1 file changed, 1 insertion(+), 1 deletion(-)`, plus a unique-line-index match |
| gh-24 (`963a66c`) | two files created, one line replaced | per-row `--stat` counts computed from block lengths, whole-file byte comparison of the created files, a *computed* `CLAUDE.md` line count, unique index |
| gh-28/29 (`b4b5d1c`) | three lines replaced in place, in both mirror copies | line-index comparison against the merge-base blob, asserting the changed set is exactly `{52, 71, 81}` |

**Three consecutive changes, three different instruments, one shared property, zero written prescription.** The property was re-derived three times; the instrument was never the same twice. That is precisely the shape line 9 already handles once — the block-to-file mapping is per change, the reader is not — and it is the shape of the answer here.

Two honest qualifications, because the case is weaker than #32 states it:

- **`git diff --stat` with asserted counts does catch a stray edit.** A fourth changed line moves the counts. So the gap is not "undetectable", it is "nowhere prescribed, and closed at three different strengths by three authors who each thought of it independently". And the objection is stronger than that, so it is stated rather than elided: all three sampled changes run `--stat` in their step 1, so the weakest form of accounting is already universal here. The three are not the same check, though. gh-26 and gh-24 assert exact insertion and deletion counts — numbers a human reads off the output and compares by eye. gh-28/29 asserts file scope only, with no counts at all. The **machine-asserted, byte-level** form, the one that fails with no reader in the loop, appeared exactly once in three changes. So what the clause upgrades is eyeballed counts to a byte-level assertion, not "no accounting" to "accounting". gh-26's counts cannot say *which* lines; gh-28/29's set can.
- **The failure has never been observed.** Zero instances of a stray edit reaching a merged change. What makes the mirror pair the right place to require the accounting anyway is the specific reason reading the diff fails there: **a stray edit applied identically to both copies looks exactly like a correct mirrored edit.** Everywhere else in the repo a doubled hunk is a smell; in the pair it is the expected shape. That is why this clause belongs in this bullet rather than being generic change hygiene.

And the one derivation that happened *inside* the pair happened by luck: gh-28/29's criterion 8 exists because a design-stage reviewer noticed, and that design's **A8** records the gap and filed this issue.

### Decision

**The property joins `Always:`; the instrument stays per change.** Block 1 is the complete new line 9.

Why not the check itself, as #32 sketches it:

- **It cannot run on half the edit shapes this bullet anticipates.** `assert len(old) == len(new)` is the load-bearing line of #32's snippet, and it dies on an insertion or a deletion — while line 9's own block clause explicitly covers insertions (*"for an insertion, directly after its anchor line"*). An `Always:` instruction that aborts on a shape named two sentences later is worse than no instruction: the author must improvise exactly the thing the rule was supposed to remove, with the rule's authority arguing against them. Created files have no base blob at all (gh-24 had two).
- **Three instruments in three changes is a measurement, not a prediction.** The variation is in the instrument and only in the instrument.
- **The property is one clause; a universal instrument is not.** Writing an instrument that covers replace, insert, delete and create would be longer than everything else in the bullet.

The clause therefore states the property and names **no** instrument. The form it states — every file the edit touches is byte-for-byte its merge-base blob with exactly the intended edit applied — is exact on all four shapes this bullet anticipates: for a replacement, put the old lines back; for an insertion, delete the inserted span; for a deletion, re-insert it; for a created file the blob is nothing, so the reconstruction is the intended text itself. Naming one shape's instrument under `Always:` would reintroduce the defect that rejects alternative (a), and would contradict the bullet's own *"Write that check per change — the block-to-file mapping and the assertions differ every time."* Byte-equality against a reconstructed base also keeps (a)'s strongest property — a stray added line trips loudly instead of quietly shifting the set — on **every** shape, with no `len(old) == len(new)` special case. That is strictly better than #32's own snippet, which needs that assert and still dies on an insertion. `CLAUDE.md` is already the file that says *"write that check per change"*; this adds one more thing the per-change check must assert, not a second mechanism.

### Rejected alternatives for #32

- **(a) `Always:` gets #32's snippet verbatim.** Rejected on the shape argument above. Its `len(old) == len(new)` assert is not incidental — #32 correctly argues it is what makes a stray added line trip loudly instead of shifting the set — so it cannot simply be dropped to generalize the check.
- **(b) A conditional — *"when the change spans few lines…"*.** Rejected twice over. It re-introduces a judgment call (*few?*) into a file whose purpose is to remove them; and the value curve it rests on is wrong. The intuition is that on a large edit the assertion degenerates into restating the diff, but it does not: the expected set comes from the **design**, the actual from the **tree**, and they are derived independently. For a 12-line insertion the design says "insert this block after this anchor", and the equivalent assertion — the file with the inserted span removed equals the base blob — is a strong statement, not a tautology.
- **(c) No rule; per-change derivation, as with the block-to-file mapping.** The strongest rejected option, and the one constraint 5 protects. It fails on three counts: the bullet names a hazard and then lists checks that do not close it, which is a defect in the document regardless of whether the hazard ever fires; the property has now been independently re-derived three times running, at three different strengths, which is the definition of a decision being re-derived; and the one derivation inside the mirror pair — the only place the argument is strongest — arrived through a reviewer's attention rather than through the rule. Per-change derivation is right for the *instrument*, and this design keeps it there.
- **(d) A shared helper in `scripts/`.** There is nothing to share. See *The `split_lines` question*.
- **(e) dev-flow's own success-criteria guidance.** The seam that would make *every* dev-flow change in *every* repo inherit the property, which is a larger and arguably better fix. Out of scope by hard constraint (`plugins/`), and rejected on merits too: the sharpest justification for the clause is mirror-pair-specific (a doubled stray edit reads as correct mirroring), and that reason does not generalize to repos with no mirror pair. Recorded, not deferred — and now filed: this design's review opened **#39**, *"CLAUDE.md: the verification rules live in the mirror-pair bullet but are applied to every change"*, and dev-flow's success-criteria guidance is one of the three candidate homes that issue has to weigh.

### The `split_lines` question

Issue #32's comment argues that a positive ruling restarts #24's accumulation on a new function, and that this design must therefore say where `split_lines` lives — inline per check, or beside `read_blocks` in `scripts/design_blocks.py`.

**Ruling: neither. The check does not need `split_lines` at all, and the rule names no helper.**

Measured, not asserted. For a line-index comparison, plain `text.split("\n")` on both sides is not merely adequate — it is strictly better than `split_lines`:

- A trailing newline yields a final `""` element on **both** sides. It compares equal, so it never enters the differing set and never shifts a reported line number. Every real line keeps its correct 1-based index either way.
- If one side's trailing-newline state *changed*, plain split makes the lengths differ and the length assert fires — a real difference, caught. `split_lines` pops the empty element from both sides and hides it.

`split_lines` exists in `check-sync.py` for a different job: making a *reported line count* agree with `wc -l` in a human-readable summary. That job does not arise in a set comparison. So the positive ruling on #32 starts no new kind:

- the rule names no helper — it names no instrument at all — and the per-change check it asks for needs none;
- the five existing copies (one in the gh-28/29 design, four in its plan, all inside that one change) stay exactly as they are — records of what was executed, under #24's *Question 2* disposition, which applies unchanged;
- if some future check genuinely needs `wc -l` agreement, it inlines four lines; and if a kind ever does form — 2+ *changes*, not 2+ heredocs inside one plan — its home is a documented module beside `read_blocks`, exactly as #24 shared the reader. **Never** `spec_from_file_location` on `check-sync.py`: the comment's reasoning is adopted in full — no `__all__`, no docstring contract, no stability commitment, and `docs/superpowers/` files are frozen records that may not be repaired when a future rename breaks them.

**The comment's drift data point is real and points the other way.** `scripts/check-sync.py` writes `if lines[-1] == "":` where every copy writes `if out and out[-1] == "":`. Verified: `str.split(sep)` with a non-`None` separator always returns at least one element (`"".split("\n")` is `['']`), so `out` is always truthy and the `out and` guard is dead code. The *copies* carry the dead branch; the source does not. This is drift in text with a null behavioural delta, and the degraded side is the copy — the opposite of the usual decay story, and evidence against a shared helper rather than for one.

**Therefore no `scripts/` change is proposed.** Adding the unreachable guard to `check-sync.py` to match the copies would make that file worse; editing the copies would falsify records.

## Issue #33 — always the minor segment

### Verified against history, not taken from the issue

Re-measured on `b4b5d1c` from the full history of both manifests:

- **`dev-flow`**: `1.0.0`, `1.1.0`, `1.2.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.3.0`, `2.4.0`, `2.5.0`, `2.6.0`, `2.7.0`, `2.8.0` — **11 bump events**, one major (the plugin split, `a104d2b`), ten minor.
- **`dev-flow-worktree`**: created at `1.2.0` by that same split, forking `dev-flow`'s then-current number, then `1.3.0` … `1.10.0` — **8 bump events**, all minor.
- The other six plugins have never moved off `1.0.0`.
- **19 bump events: 18 minor, 1 major, 0 patch.** No non-zero patch segment has ever existed. `git grep -in 'semver\|patch version\|minor version\|patch segment' -- CLAUDE.md CONTEXT.md docs/ ':!docs/superpowers/'` returns nothing, and `git grep -in bump` outside `docs/` returns exactly one line: `CLAUDE.md:7`.

Two corrections to the issue, neither of which changes its conclusion:

- **`marketplace.json` carries no `version` field at all** (`grep -c version .claude-plugin/marketplace.json` → `0`). The issue's "every version string ever written to a `plugin.json` or `marketplace.json`" over-states the surface; versions live only in `plugins/*/.claude-plugin/plugin.json`.
- **The count is now 19, not 15.** The issue was filed before 2026-08-02; four bump events landed that day.

### The evidence the issue does not have

1. **Four bumps in one day.** `9a5cab2` (PR #35) took `dev-flow` 2.6.0 → 2.7.0 and `dev-flow-worktree` 1.8.0 → 1.9.0; `b4b5d1c` (PR #37) took them to 2.8.0 / 1.10.0. All four minor.
2. **The issue's central empirical claim is now false.** It states: *"There has never been a purely-editorial bump in either direction, because the repo has never had one."* #37 is one. It changed three lines per copy, each a one-word rename of a concept (`group-resolution agent` → `resolver`), and its own design says: *"Patch is the more literal semver reading — no rule, trigger, contract, or provenance format changes; the protocol says the same thing under one name instead of three."* It bumped **minor**, on uniform precedent plus *"adopting a minor-vs-patch convention is a repo-policy decision whose home is `CLAUDE.md`, which this change is scoped out of"*.
3. **So the question has now been re-derived twice in consecutive changes** — #30's design-stage review (which the issue says *"could not settle it from anything written down"*) and #37's design, which spent a ~150-word paragraph on it. Both landed on minor. Both explicitly named `CLAUDE.md` as the missing home and both were scoped out of it. That is the cost of not writing it down, paid twice, measured, in one day.

The first purely-editorial-shaped change the repo has ever had took minor and had to argue for it. There is nothing left to learn by waiting for a second one.

### Decision — option 1, minor always

Block 0 is the complete new line 7. The reasoning, in the order it should be weighed:

- **Nothing reads the segment.** The install cache path is the exact version string; `marketplace.json` carries no version and therefore no range; nothing in the repo or in `claude plugin validate` resolves version ranges. A patch bump busts the cache exactly as well as a minor one. Choosing minor-always forfeits nothing mechanical — only a signal.
- **The signal cannot be produced reliably here.** These plugins ship prose that a model reads as its instructions; the text *is* the program. "Editorial" is not a distinction that survives contact with a real case here: #37's three one-word renames were the cleanest editorial candidate this repo will ever produce, and its resolver still had to argue whether renaming a concept inside a prompt changes what the model does. A test whose clearest instance is contestable is not a test — it is a per-change judgment wearing a rule's clothes, which is the exact latent regression the issue names.
- **Precedent is unanimous and free to keep.** 18 of 18 non-major bumps are minor. Writing down what has always happened costs one clause and forecloses re-derivation; it introduces no migration and invalidates no existing version.
- **Version numbers are not scarce.** The only cost of minor-always is that the minor segment burns fast — four in a day. That is a cost of nothing.

Major stays named because "always minor" alone would be literally false about the one major this repo has (`a104d2b`) and would forbid the next plugin split. Nothing else about major needs saying.

### Rejected alternatives for #33

- **(2) Patch for editorial, minor for behavioural.** The genuinely attractive option — it carries information, and `CLAUDE.md` already draws a behavioural line for *whether* to bump, so reusing it for *how much* looks free. Rejected on the measured cost of its test, twice observed: #30 and #37 both tried to apply it informally and neither could settle it from the artifact alone. And the boundary is not merely hard, it is ill-defined for this product: every shipped byte is model input, so "no behavior changed" is a claim about a model's response to a prompt edit, which nothing in this repo can check. The written test such a rule would need is longer than the rule it replaces, and it would still be adjudicated per change.
- **(3) Say nothing on purpose.** As the issue argues, this collapses into (1) with the ruling unstated — and "unstated" is exactly what produced two re-derivations in one day. Strictly worse than (1).
- **Close as not worth a rule.** This was live, and it is the outcome constraint 5 protects. What defeats it is not the failure mode — a version one segment off has no mechanical consequence, and the issue is right about that — but the *cost of the question*. Two designs in one day spent real reasoning on it and both ended by pointing at this file. The bar is "a rule that stops a decision being re-derived earns its line"; this one arrives with receipts, and the clause costs 48 words.
- **An ADR.** Out of scope by constraint, and not warranted anyway. ADR-0001, -0002 and -0003 record architecture decisions with live consequences (a duplication policy, a model-tier change, a topology invariant). "Which segment moves" is a convention with no consequence beyond the log. The rule's home is `CLAUDE.md` and its reasoning is this document — the same disposition #24 reached for the same reason.

## The concurrent-bump collision is a separate concern

The evidence, verified first-hand in this checkout rather than taken from the dispatch:

- `4e672e2` on `tayl0r/gh-30-flat-topology` and `5f99cf2` on `tayl0r/gh-28-29-review-prose` **both** bumped `2.6.0` → `2.7.0` and `1.8.0` → `1.9.0`.
- `84d8cc9` merged `origin/main` into the second branch after the first had landed. The merge's diff against its first parent contains **no `plugin.json` row at all** — both sides had made the identical change, so git had nothing to flag — and `git show 84d8cc9:plugins/dev-flow/.claude-plugin/plugin.json` reads `2.7.0`, a number `main` had already published *without* that change's `SKILL.md` text. The version-keyed cache would never have picked it up.
- `02ffb7b` re-targeted to `2.8.0` / `1.10.0` once someone noticed. Its message records that **none of that change's eight success criteria caught it**, because none compared against the *published* version.

This is a versioning failure with a real mechanical consequence — the precise consequence line 7's existing sentence exists to prevent — unlike the one-segment-off failure #33 names, which has none.

**Ruling: out of scope for #33, filed as its own issue.** Three reasons, in order:

1. **Different question, different shape of answer.** #33 asks how a contributor writes a number. This asks *against which baseline* the number is derived, and how a machine detects that it wasn't. The first is a convention sentence; the second is a check. Appending the second to line 7 would put a defect fix inside a taxonomy rule and let the taxonomy question's low stakes set its priority.
2. **The best home for that check is probably a file this change may not touch.** The assertion that wants running is *"the new version is strictly greater than `origin/main`'s"*, evaluated at merge time — which points at dev-flow's merge gate (`plugins/`, hard out of scope here) or at CI, where the PR base ref is available. `scripts/check-sync.py` is the wrong host and should not be reached for: it compares in-tree facts only, has no remote, would fail in a fresh clone with no fetched `origin/main`, and on `main` itself the version legitimately *equals* `origin/main`'s. Choosing between those homes needs its own evidence, and doing it inside #33 would either smuggle scope or settle for a knowingly second-best home.
3. **It is a defect; #33 is a convention.** Keeping them apart keeps each one's reasoning legible.

**The pipeline files it at integration** (A6), with the evidence above. One honest cross-link belongs on that issue and is recorded here rather than left for the next reader to find: **the minor-always ruling makes the collision deterministic rather than probabilistic.** Two concurrent changes now always target the same next number, where a patch/minor split would sometimes have produced differing values and hence a visible merge conflict. That is *not* an argument for the split — two concurrent behavioural changes collide under any rule, and a conflict that only appears when the values happen to differ is a coincidence, not a mechanism — but it does raise the new issue's priority, and the new issue should say so.

Nothing about this change's own edits touches a version, so the collision cannot bite this branch.

## The edit

Two whole-line replacements in `CLAUDE.md`. Whole-line replacement is the gh-7 and gh-24 precedent for this file and is the stronger check: an exact whole-line match at a known index cannot be satisfied by a fragment landing in the wrong bullet.

Both blocks were produced by applying the substitution to the file on disk in `python3` and printing the result — not retyped — so every byte outside the added spans is carried over from `b4b5d1c` verbatim. *Verification* step 2 re-proves that from git rather than trusting it.

### Block 0 — the complete new `CLAUDE.md` line 7 (issue #33)

Replaces line 7 in full. The bullet's two existing sentences are unchanged; everything from `**Always the minor segment**` onward is new, so this is a **pure append**.

```
- **Bump `version` in `plugins/<name>/.claude-plugin/plugin.json` on any behavior change.** The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so an edit at an unchanged version is never picked up on re-sync. **Always the minor segment** — `1.4.0 → 1.5.0`. Nothing reads the segment (the cache keys the whole string), and for prose a model reads there is no stable editorial-versus-behavioural line for a patch to mark. Major only when a plugin is split or renamed (`dev-flow` 1.x → 2.0.0).
```

The example is `1.4.0 → 1.5.0`, a number neither plugin currently sits at, so it cannot be misread as an instruction to bump to a particular version.

**This edit removes no phrase**, so `CLAUDE.md`'s existing `Always:` grep has nothing to search for on this line. *Verification* step 2 asserts the base line 7 is a strict prefix of block 0 instead, which is the stronger statement for an append.

### Block 1 — the complete new `CLAUDE.md` line 9 (issue #32)

Replaces line 9 in full. Everything before `**Always:**` and everything from `**When the change has a design doc**` onward is byte-identical to the line #24 landed at `963a66c`. The span between those two markers is a single sentence in the base; block 1 replaces it with a longer sentence plus one new one — *"The other checks here prove that edit landed; only this one proves nothing else did"* — which says what the new assertion adds over its siblings.

```
- **Some files are mirrored across `dev-flow` and `dev-flow-worktree` and must be edited in both.** `python3 scripts/check-sync.py` enforces what can be enforced mechanically — the `adversarial-review/SKILL.md` pair (line-for-line identical after `dev-flow-worktree` → `dev-flow`, minus declared exceptions) and the `description` duplicated between each `plugin.json` and `.claude-plugin/marketplace.json`. It runs on every PR. The pipeline `SKILL.md` pair and the two `README.md`s are too divergent to check mechanically — mirror those by hand. **`check-sync.py` proves the two copies agree with each other, never that either is correct**: text mangled identically in both sides passes it, and so does an edit missed on both. So any change to a mirrored pair, machine-checked or hand-mirrored, must also verify against something *outside* the pair. **Always:** grep for the exact phrases the edit removes, expecting no hits, and assert that every file the edit touches is byte-for-byte its merge-base blob (nothing, for a file it creates) with exactly the intended edit applied. The other checks here prove that edit landed; only this one proves nothing else did. **When the change has a design doc** that gives replacement or inserted text as fenced blocks: also add a short `python3` check that re-reads those blocks from the design on disk, never retyped, asserting each appears verbatim in its target and, for an insertion, directly after its anchor line. Write that check per change — the block-to-file mapping and the assertions differ every time, so there is no shared runner to call. The *reader* is not per change: run `python3 scripts/design_blocks.py <design>` to get the block shape and indices, then have the check `sys.path.insert(0, "scripts")` and call `read_blocks(<design>, <shape>)` — it re-reads the blocks and exits non-zero if the shape moved — instead of re-typing the reader.
```

The exact phrase this edit removes, for the residue grep, is the sentence junction:

```text
expecting no hits. **When the change
```

Pure ASCII, and `git grep -F` finds it at exactly one place outside `docs/superpowers/` today.

## Length budget

`CLAUDE.md` is read in full by every contributor and every agent working this repo, so length has a real cost and any addition must be paid for. Line 7 goes **28 → 76 words**; line 9 goes **246 → 286**. The file stays **29 lines**.

The search for offsetting cuts was run and found nothing worth taking; it is recorded here so it is not re-run:

- **Line 9's tail** — the `design_blocks.py` discovery command and call form, ~55 words — is the obvious target and is refused. It landed three commits ago at `963a66c` as a designed artifact with its own conformance check, it is the one span a call-site author needs verbatim, and rewriting it would put freshly reviewed text back into play to reclaim perhaps fifteen words.
- **The `check-sync.py` proves … never that either is correct** sentence and its two examples are the motivation the new clause depends on. Cutting them to pay for the clause is circular.
- **Line 7's two existing sentences** are the rule and its mechanical reason, in 28 words. There is nothing to cut.

So both additions are net new length. Each is justified against the stated bar — not "restates judgment everyone already applies" but "stops a decision being re-derived" — and each arrives with receipts: three instruments across three consecutive changes for #32, two full re-derivations in a single day for #33. No size comparison flatters the result — after the edit line 7 is the section's second-longest bullet — so the case rests on the receipts, not on the size of what was added.

## Assumptions

- **A1.** Lines 7 and 9 are the targets as of `b4b5d1c`. The implementation matches on **text**, not line number: it halts if the current line 7 is not a prefix of block 0, or if the current line 9 is not block 1 with the `Always:` sentence replaced.
- **A2.** Nothing in the toolchain resolves version *ranges* — the cache path is the exact string, and `marketplace.json` carries no version field (both verified). The minor-always ruling is a ruling about a segment nothing reads; if a consumer that resolves ranges ever appears, revisit it, because the premise changes.
- **A3.** No test framework exists in this repo. *Verification* is the whole surface.
- **A4.** `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state, per `CLAUDE.md`.
- **A5.** **Neither issue is a no-change ruling.** Both #32 and #33 ship text and both close on merge, so there is no separate issue-close comment to write for either — the PR body carries both rulings. If a review flips either to no-change, that issue's section above becomes its closing comment verbatim and the corresponding block is dropped from the change.
- **A6.** The concurrent-bump collision is filed as its own GitHub issue by the pipeline at integration, from *The concurrent-bump collision is a separate concern* — not part of the implementation, and it touches no file in the authorized set. The filer dedupes against open issues first. Suggested title: **"Concurrent branches derive their version bump from the branch base, so a merge can silently reuse a published version"**; it refs #33 and #37 and must carry the cross-link about minor-always making the collision deterministic.
- **A7.** Text assertions use `git grep`, not bare `grep` — under Claude Code's Bash tool bare `grep` is a ugrep-backed shell function whose output layout is not reliable for per-file assertions. Whole-line and index assertions are made in `python3`, where they are exact.
- **A8.** This change is **not itself a mirrored-pair change** — `CLAUDE.md` is enrolled in no pair — so its own new `Always:` clause does not bind it. *Verification* steps 2 and 5 apply it anyway, as the rule's first exercise; that is voluntary, and stated so nobody reads it as the rule's scope widening to every file.
- **A9.** This design's own plain fenced blocks are blocks 0 and 1, shape `[1, 1]`. No *Verification* expectation is a function of a block's *length* except that shape, so a review that rewrites either block's text leaves every check below runnable as written; a review that splits one into two lines trips step 0, which halts. *Length budget*'s word counts are the one exception — they are measured from the blocks with `len(block.split())` and must be re-measured whenever a block's text changes.
- **A10.** This change's design review filed three issues, all of which already exist and none of which is part of this implementation or touches a file in the authorized set: **#39**, *"CLAUDE.md: the verification rules live in the mirror-pair bullet but are applied to every change"* (the placement question recorded under *Rejected alternatives for #32* (e)); **#40**, *"dev-flow: Command discipline binds the pipeline's own git commands but not the Verification blocks designs emit"* (why every base-consuming step here runs its `git` calls through `python3` `argv` rather than a shell chain); and **#41**, *"dev-flow: designs hand-type measurements of their own text, and the spec self-review certifies them unchecked"* (why A9 now names *Length budget*'s counts as the one measured thing).

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`CONTEXT.md`** — a concurrent change owns it, and nothing here wants it. This change coins no repo concept: *minor segment*, *merge-base blob* and *line-index comparison* are standard vocabulary, not shapes this repo reasons about, and `CONTEXT.md` defines shapes rather than one row per word. A conclusion, not a deferral.
- **`plugins/`, `.claude-plugin/`, and every `plugin.json`** — a concurrent change owns `plugins/`, and **no version is bumped**. `CLAUDE.md` sits outside `plugins/`, ships into no cache, and is read at edit time rather than into any model invocation, so the version-keyed-cache rule does not fire. This is a conclusion, not a deferral; *Verification* step 8 asserts it because the reflex is to bump.
- **`scripts/`** — no change. `design_blocks.py` is *used* by the conformance check and not modified. `check-sync.py` is not touched: the `out and` guard question resolves to "the copies carry the dead branch, not the source", so matching them would make the source worse (*The `split_lines` question*).
- **The five existing `split_lines` copies** in the gh-28/29 design and plan — records of what was executed; #24's *Question 2* disposition applies unchanged.
- **`docs/adr/`** — outside the authorized file set, and no ADR is warranted for either ruling (*Rejected alternatives for #33*).
- **The concurrent-bump collision** — its own issue (A6).
- **`.claude-plugin/marketplace.json`** — untouched. No `description` changes, so `check-sync.py`'s Check A is unaffected, and Check B's mirror pair is not in this change at all.
- **Every pre-existing file under `docs/superpowers/`** — prior records, including the passages quoted here.

## Verification

Every command runs from the repo root. The base is `git merge-base origin/main HEAD` — never a hardcoded SHA, so it stays correct if `main` advances or the branch is rebased. It resolves to `b4b5d1c` today. Steps run after the edit unless stated. Every step that consumes the base — 1, 2 and 5 — computes it inside `python3` and passes it to `git` as an `argv` element, never through a shell. That is deliberate: `git merge-base` prints nothing to stdout on failure — exit 128 for an unresolvable ref, exit 1 and no message whatsoever when the histories share no ancestor — so in a shell an unquoted `$(…)` silently degrades a base comparison into a working-tree-vs-index one, which in a repo that commits per task passes. `argv` has no word-splitting to exploit, so the hazard is gone by construction rather than by remembering to quote; step 1 works the reasoning out in full.

**0. Block shape.** Expect `shape: [1, 1]`, with block 0 previewing the bump bullet and block 1 the mirrored-pair bullet. Anything other than two entries means this design was edited after the plan captured its shape — **stop and report**:

```sh
python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md
```

**1. File scope — exactly one file, and it is not a plugin file.** Expect a `base:` line carrying a 40-character SHA (`b4b5d1c…` today), a single stat row ` CLAUDE.md | 4 ++--` with the summary `1 file changed, 2 insertions(+), 2 deletions(-)` and no other row, then `file scope: OK` and `exit=0`. This step is a `python3` heredoc rather than a shell `&&` chain, and that is the substance of the step rather than a style choice. `git merge-base` writes nothing to stdout when it fails — exit 128 for an unresolvable `origin/main`, and exit **1 with no message at all** for histories sharing no ancestor — so in a shell an unquoted `$(…)` vanishes by word-splitting and degrades both comparisons into working-tree-vs-index ones, which in a repo that commits per task are empty: measured, that form prints a pass token and exits 0 on an arbitrarily broken branch. dev-flow's **Command discipline** answers this by asking every caller to *"capture, validate non-empty, and quote any command output a later command consumes"* — a rule each caller must remember. Passing the base as an `argv` element retires the hazard **by construction** instead: there is no shell, so nothing can word-split, and an empty base is `fatal: bad revision ''` rather than a different valid command. The shell form also carries an environment-level failure the `python3` form does not — a chain that captures a ref and reuses it across `&&`-joined `git` commands is **refused unrun** by Claude Code's Bash tool under worktree isolation (*"too complex to verify that it stays inside the worktree"*), and this repo's runs happen in linked worktrees, so a check written that way may never execute at all. Steps 2 and 5 already run their base-consuming `git` calls through `argv`, and A7 already rules that exact assertions belong in `python3`; this step was the one holdout, and the `argv` form is now uniform across all three. The `--name-only` equality is the machine-checked form of this step's headline claim, and it prints the set it actually found, so a failure names the offending path; `--stat` is for reading, since its column widths shift when a second file appears and its text is therefore not a safe assertion. There is deliberately **no separate `--quiet` assertion** over `plugins/`, `.claude-plugin/`, `scripts/`, `CONTEXT.md`, `docs/adr/` and `.gitignore`: all six lie inside `. ':!docs/superpowers/'`, so the equality already implies every one of them is untouched — checked against all six — and `--quiet` prints nothing whatever, on success or on failure, so it can neither name a path nor add a detection. In an `&&` chain it was also unreachable on the very reflex it was kept for: a version bump fails the equality one line earlier and short-circuits it. The local `git` wrapper raises with the failing command, its exit status and git's own message, so a broken base fails in one quotable line; steps 2 and 5 keep `check=True`, where the documented red output is a `MISMATCH:` line and a producer failure is only the escape hatch, while here the producer failure *is* a documented red case and a traceback carries machine-specific paths no expectation could quote:

```sh
python3 - <<'PY'
import subprocess, sys
SCOPE = ["--", ".", ":!docs/superpowers/"]
WANT = ["CLAUDE.md"]
def git(*args):
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("FAILED: git %s -- exit %d, %s"
                         % (" ".join(args), r.returncode, r.stderr.strip() or "(no message)"))
    return r.stdout
base = git("merge-base", "origin/main", "HEAD").strip()
print("base:", base)
print(git("diff", "--stat", base, *SCOPE), end="")
changed = [p for p in git("diff", "--name-only", base, *SCOPE).split("\n") if p]
if changed != WANT:
    print("file scope: FAIL -- changed %s, want %s" % (changed, WANT))
    sys.exit(1)
print("file scope: OK")
PY
echo "exit=$?"
```

Run it once **before** the edit to watch it discriminate; the red output is `file scope: FAIL -- changed [], want ['CLAUDE.md']` and `exit=1`. A base that cannot be computed fails as a single line naming the command, its exit status and git's message — for histories sharing no ancestor, where git itself says nothing, that line reads:

```text
FAILED: git merge-base origin/main HEAD -- exit 1, (no message)
exit=1
```

The `':!docs/superpowers/'` pathspec is required: this design's front-matter sets `docs: commit`, so this run's own design and plan are committed on this branch and an unfiltered diff necessarily reports them.

**2. Design conformance, through the shared reader.** This is the check `CLAUDE.md` requires. It re-reads both blocks from this design on disk — never retyped — and re-reads the *pre-change* lines from git, so nothing in it is typed twice. It asserts: block 0 is `CLAUDE.md` line 7 exactly and uniquely; block 1 is line 9 exactly and uniquely; the file gained and lost no lines (29 before and after, per `wc -l`); the base line 7 is a strict prefix of block 0 (the append kept every existing byte); and the base line 9's head and tail — everything before `**Always:**` and everything from `**When the change has a design doc**` — both survive in block 1 (the rewrite touched only the span between those two markers). Both this step and step 5 split on `"\n"` with no helper, so a file ending in a newline yields one extra empty element — present identically on both sides, and only ever printed in a failure message. **The fence is unindented on purpose** — a `python3` heredoc indented under a list item is an `IndentationError`. Both markers are located with `partition`, so a base whose line 9 lost either one reports `MISMATCH:` and exits 1 like every other failure path rather than raising. That is not hypothetical: the base is computed rather than hardcoded precisely so it survives `main` advancing or a rebase, and a base that moved is the one state in which these anchors can be missing — gh-28-29's base moved under it mid-flight four days ago. Failures of the *producers* — `git`, `read_blocks` — are deliberately left to raise as themselves: they name the failing command, which is more useful than a `MISMATCH:` line, and no traceback can be mistaken for a pass.

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from design_blocks import read_blocks
DESIGN = "docs/superpowers/specs/2026-08-02-gh-32-33-claude-md-conventions-design.md"
HEAD_END = "**Always:**"
TAIL_START = "**When the change has a design doc**"
base = subprocess.run(["git", "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
old = subprocess.run(["git", "show", base + ":CLAUDE.md"],
                     capture_output=True, text=True, check=True).stdout.split("\n")
new = Path("CLAUDE.md").read_text(encoding="utf-8").split("\n")
b0, b1 = read_blocks(DESIGN, [1, 1])
bad = []
if len(new) != len(old):
    bad.append("CLAUDE.md gained or lost lines: %d against the base's %d" % (len(new), len(old)))
for label, block, want in (("block 0", b0[0], 7), ("block 1", b1[0], 9)):
    at = [i + 1 for i, l in enumerate(new) if l == block]
    if at != [want]:
        bad.append("%s matches CLAUDE.md at lines %s, want exactly [%d]" % (label, at, want))
if not b0[0].startswith(old[6]):
    bad.append("base line 7 is not a prefix of block 0; the bump bullet is not a pure append")
if not b0[0][len(old[6]):].startswith(" **Always the minor segment**"):
    bad.append("block 0 appends something other than the minor-segment clause")
head, sep, tail = old[8].partition(TAIL_START)
pre, always, _ = head.partition(HEAD_END)
if not sep:
    bad.append("base line 9 does not contain %r" % TAIL_START)
elif not always:
    bad.append("base line 9 does not contain %r before %r" % (HEAD_END, TAIL_START))
else:
    if not b1[0].startswith(pre):
        bad.append("block 1 changes text before the Always: sentence")
    if not b1[0].endswith(sep + tail):
        bad.append("block 1 changes text from %r onward" % TAIL_START)
for why in bad:
    print("MISMATCH:", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

Expect exactly `design-conformance: OK` and `exit=0`. Run it once **before** the edit to watch it discriminate; the red output is:

```text
MISMATCH: block 0 matches CLAUDE.md at lines [], want exactly [7]
MISMATCH: block 1 matches CLAUDE.md at lines [], want exactly [9]
design-conformance: FAIL
exit=1
```

If the shape guard trips instead (`design code-block shape is …`), **stop and report**: this design was edited after the plan captured its shape.

**3. Residue — the removed junction is gone from the tree.** Expect no output and a non-zero exit. The pathspec is required: this design quotes the phrase.

```sh
git grep -n -F 'expecting no hits. **When the change' -- . ':!docs/superpowers/'
```

**4. Presence — both new clauses are in `CLAUDE.md`, once each.** Expect `CLAUDE.md:1` for each:

```sh
git grep -c -F 'Always the minor segment' -- CLAUDE.md
git grep -c -F 'byte-for-byte its merge-base blob' -- CLAUDE.md
```

**5. The change's own changed-line set is exactly `{7, 9}`.** This is one instrument that satisfies the property block 1 states — the clause names none — run on this change's own edit, voluntary since `CLAUDE.md` is in no mirror pair (A8), and it is the clause's first exercise. Plain `split("\n")` is used on both sides deliberately, with no `split_lines` helper: the trailing element is present on both sides and compares equal, and a trailing-newline change would trip the length assert rather than being hidden (*The `split_lines` question*). The set is printed `sorted`, since a Python set of small integers prints in hash order (`{7, 9}` renders as `{9, 7}`) and an expectation should not depend on that. Expect `changed lines: [7, 9]` and `line-set: OK`. Steps 2 and 5 together are exactly the reconstruction the new clause asks for — step 2 proves the intended edit is what landed on lines 7 and 9, step 5 proves no other line moved — so this change exercises its own new rule end to end, which is what A8 means by a voluntary first exercise. **The fence is unindented on purpose.**

```sh
python3 - <<'PY'
import subprocess, sys
from pathlib import Path
base = subprocess.run(["git", "merge-base", "origin/main", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
old = subprocess.run(["git", "show", base + ":CLAUDE.md"],
                     capture_output=True, text=True, check=True).stdout.split("\n")
new = Path("CLAUDE.md").read_text(encoding="utf-8").split("\n")
if len(old) != len(new):
    print("LENGTH: base %d lines, working %d" % (len(old), len(new)))
    sys.exit(1)
changed = {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}
print("changed lines:", sorted(changed))
print("line-set:", "OK" if changed == {7, 9} else "FAIL")
sys.exit(0 if changed == {7, 9} else 1)
PY
echo "exit=$?"
```

Before the edit this prints `changed lines: []` and `line-set: FAIL`, which is the red run.

**6. `python3 scripts/check-sync.py`** — passes, with output identical to before the change. Expect `check-sync: all checks passed` and `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`. It reads none of the changed files.

**7. `claude plugin validate .`** — exit 0, exactly 8 `No author information provided` warnings, no errors.

**8. No version moved.** Expect `dev-flow` at `2.8.0` and `dev-flow-worktree` at `1.10.0`, each labelled with its own path:

```sh
git grep '"version"' -- plugins/dev-flow/.claude-plugin/plugin.json plugins/dev-flow-worktree/.claude-plugin/plugin.json
```

## Files the plan will touch

- **Modify:** `CLAUDE.md` line 7 (block 0, verbatim, whole-line replacement) and line 9 (block 1, verbatim, whole-line replacement). Nothing else in the file.
- **Committed by dev-flow per `docs: commit`:** this design and its plan under `docs/superpowers/`.

Nothing else. No `scripts/` file, no plugin file, no `plugin.json`, no `CONTEXT.md`, no `docs/adr/`, no `.gitignore`.

## PR

```text
Close #32 and #33 by writing down two conventions CLAUDE.md left to judgment.

#32 -- mirrored-pair verification. The bullet names the failure it cannot
catch ("text mangled identically in both sides passes it") and then prescribes
two checks that do not close it. The last three changes each proved "nothing
else moved" anyway, with a different instrument each time (stat counts, whole-
file compare, a line-index set) and nothing written down. The property joins
the Always: list in a form exact on all four edit shapes -- every file the
edit touches is byte-for-byte its merge-base blob, with exactly the intended
edit applied -- and no instrument is named. Naming one shape's instrument
under Always: is the defect that rejects #32's own snippet: it asserts equal
line counts, so it cannot run on an insertion, a deletion, or a created file
-- shapes the same bullet already anticipates.

No scripts/ change. The line-set check needs no split_lines helper: plain
split("\n") is equivalent for a set comparison and strictly better, since a
trailing-newline change trips the length assert instead of being hidden. The
drift the issue reports (check-sync.py's `if lines[-1] == ""` vs the copies'
`if out and out[-1] == ""`) is a dead guard -- str.split with a non-None
separator always returns at least one element -- and the copies are the side
carrying it.

#33 -- how much to bump. 19 bump events across the repo's history: 18 minor,
1 major, 0 patch. Nothing reads the segment (the cache keys the whole string),
and for plugins whose product is prose a model reads there is no stable
editorial-versus-behavioural line for a patch to mark -- #37, the first
purely-editorial-shaped change this repo has had, still had to argue it and
still chose minor. The rule is now written: always the minor segment, major
only when a plugin is split or renamed.

CLAUDE.md lines 7 and 9, whole-line replacements, 29 lines before and after.
No plugin file is touched and no version is bumped: CLAUDE.md ships into no
cache.

Filed separately, not folded into #33: two concurrent branches both bumped
2.6.0 -> 2.7.0, and merging main auto-resolved the version line with no
conflict, which would have shipped new skill text at an already-published
version. That is a defect with a mechanical consequence and its fix is a check
whose likely home is dev-flow's merge gate or CI, not a convention sentence.

The design review filed three more, none of them implemented here: #39, the
verification rules live in the mirror-pair bullet but are applied to every
change; #40, dev-flow's Command discipline binds the pipeline's own git
commands but not the Verification blocks designs emit; #41, designs hand-type
measurements of their own text and the spec self-review certifies them
unchecked.

Closes #32
Closes #33
```

## Spec self-review

- **Placeholders / TBDs:** none. Both replacement lines are given in full as plain fenced blocks; every command is runnable as written with its expected output; the deferred issue has a title and its evidence.
- **Internal consistency:** block 0 is the base line 7 plus one appended clause and nothing else; block 1 is the base line 9 with only the `Always:` sentence rewritten. Both were produced by substitution on the file on disk rather than retyped, and *Verification* step 2 re-derives the untouched spans from git rather than trusting that. The word counts in *Length budget* and the `29 lines` invariant are consistent with two whole-line replacements and with shape `[1, 1]`; A9 states which numbers a review edit to a block's text can leave stale — the word counts, and only those — and how to re-measure them.
- **Scope:** one file, two lines. Step 1 checks it by file, step 5 by line. `CONTEXT.md`, `plugins/`, `scripts/`, `docs/adr/` and the version bump are each named in *Out of scope* with the reason, and each is a conclusion rather than a deferral.
- **Ambiguity:** the one place a fresh implementer could go wrong is grep scope — the removed junction and both new clauses legitimately appear in this document. Called out at each point of use with the `':!docs/superpowers/'` pathspec.
- **Positions taken:** #32 ships, narrowed to the property and to a form exact on all four edit shapes; **no instrument is named**, because naming one shape's instrument under `Always:` is the defect that rejects #32's own snippet. #33 ships as minor-always, with major named only for a plugin being split or renamed. The `split_lines` question resolves to "no helper is needed". Hoisting the clause out of the mirror-pair bullet is **#39**'s charter, not this change's. The concurrent-bump collision is ruled a separate concern and filed, not designed here; #39, #40 and #41 were filed by this design's own review and are likewise not implemented here (A10). No question is left open and nothing is left for the implementer to decide.
