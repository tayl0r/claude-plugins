---
dev-flow:
  slug: gh-54-name-removed-phrase-grep
  stops: [pre-merge]
  docs: commit
---

# gh-54 — give the removed-phrase grep a canonical name across both its shipped mentions (`CLAUDE.md` + ADR 0001)

Close **#54** by coining a canonical name — **the removed-phrase grep** — for the one `## Verifying a change` rule that had none, and using it in both places the check is named in shipped text. Insert it as a short bold appositive into the existing `**Always:**` bullet of `CLAUDE.md`'s `## Verifying a change` section, and align the check's one other shipped mention — `docs/adr/0001-duplicate-the-two-dev-flow-variants.md:9`, which still calls it "the residue-grep" — to that same name. No plugin is touched, no `SKILL.md` is touched, and the issue's original pipeline-general question is recorded as **answered-no**.

This is a two-file documentation change of two lines: a 30-byte insertion into `CLAUDE.md` and a one-word swap (`residue-grep` → `removed-phrase grep`) in the ADR. Nothing else moves.

## Problem / Context

### The revised scope is the owner's update comment, not the original issue body

Issue #54 was filed as a *question*: does the removed-phrase grep — the one `## Verifying a change` rule that names no repo-local instrument — warrant a pipeline-general statement in `plugins/`, so it binds dev-flow runs in other repos too? The repo owner's UPDATE COMMENT (posted 2026-08-03, after #39/#57 merged at `52c3883`) is the authoritative brief and revises the scope decisively:

1. **The pipeline-general question is answered NO.** A `plugins/` bullet would ship permanent per-invocation prose into other repos to solve a problem they do not have.
2. **What is worth doing:** give the check a canonical name inside the existing clause — the owner estimates about five words — because the check has drifted across three different labels and that drift once produced a genuinely wrong count.

### The answered-no record (13-repo measurement cited from the issue comment, not re-run here)

Per the owner's update comment (the source of these figures; **not re-measured in this design**):

- **13 repos** outside `claude-plugins` carry `docs/superpowers/` artifacts, holding roughly **90 design and plan docs** between them.
- Grepping all of them for the removed-phrase vocabulary — `expecting no hits`, `removed phrase`, `residue` — returns **zero hits**. The check has never been written outside this repo.
- The reason is not that dev-flow failed to propagate it: most of those repos have real test suites (npm / Cargo), where a dangling reference to deleted text breaks the build for free. The removed-phrase grep only earns its keep in a pure-prose repo where text assertions *are* the correctness surface — and `claude-plugins` is the only such repo.

So a pipeline-general bullet would burden ~13 repos with per-invocation prose to solve a problem 12 of them do not have. The question is closed **answered-no**, with that 13-repo measurement as the record.

### The naming drift is the actual, measured symptom (cited from #39's design)

The removed-phrase grep is prescribed by every prose change this repo makes, but under three different names. Per `docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md` (its measurement table and the note beside it — cited, not re-run here):

- Across **ten designs**, all ten prescribed the check, under one of three labels: *residue*, *removed phrase*, and the clause's own *expecting no hits*.
- A first draft of #39's own measurement counted **9 of 10** because its search predicate matched only two of the three labels; widening it to the third (`a94f60a`'s *"Removed phrase"*) corrected it to 10 of 10.

That is a naming drift that has already produced one wrong number — concrete demand for a single canonical name, not speculation.

### The two shipped mentions of the check, both measured here

The check is named in exactly two places in this repo's *shipped* (non-`docs/superpowers/`) text; this change aligns both. Two facts I verified with commands while drafting this design:

- The clause's current location is **`CLAUDE.md:16`** at this branch's HEAD. The owner's comment cites *line 15* (accurate at `52c3883`); two clause-touching PRs merged since (gh-51/55, gh-66) added lines to the same section and pushed it down by one. Command: `git grep -n -E 'removed[ -]phrase|residue|expecting no hits' HEAD` prints `HEAD:CLAUDE.md:16:- **Always:** grep for the exact phrases the edit removes, expecting no hits, …`. **Anchor the edit by its unique text, not by the line number.**
- `docs/adr/0001-duplicate-the-two-dev-flow-variants.md:9` calls the check *"the residue-grep"* — a live, present-tense pointer under the ADR's `## Consequences`: *"Changes touching it must carry their own verification — see the residue-grep and design-conformance rules in `CLAUDE.md`."* It routes a future contributor to a rule *by name*, so once the canonical name exists it is drift by definition to leave this on a rejected alias. `git grep -n -i 'residue' HEAD -- . ':(exclude)docs/superpowers'` returns **exactly this one line** — so the ADR is the *only* other shipped home of the concept, and aligning it closes the seam completely (the `residue` hits under `docs/superpowers/` are dated dev-flow artifacts — history, correctly untouched, and the removed-phrase grep below is file-scoped away from them).

## Decision

### Canonical name: **the removed-phrase grep**

Coin `the removed-phrase grep` as the check's one name, and weave it into the clause as a bold appositive placed immediately after the phrase it names (`… expecting no hits (the **removed-phrase grep**), and assert …`). The name echoes the clause's own noun — the sentence already says "the exact **phrases** the edit removes" — so name and definition are self-consistent in situ, and it matches the issue title, the owner's comment (which uses it, in bold, repeatedly), and #39's design. The ADR's mention is a *reference* to this rule rather than the defining site, so it takes the same name unbolded (the ADR reserves bold for "mirror pair"/"hand-mirrored pair"; its "residue-grep" and "design-conformance" are already plain).

### Anchor 1 — the `CLAUDE.md` clause

Replace exactly one line: the `**Always:**` bullet of `## Verifying a change`, currently **`CLAUDE.md:16`** at this branch's HEAD (anchor by content, not line number — see above). Its current text is:

```text
- **Always:** grep for the exact phrases the edit removes, expecting no hits, and assert that every file the edit touches is byte-for-byte its merge-base blob (nothing, for a file it creates) with exactly the intended edit applied. The other checks here prove that edit landed; only this one proves nothing else did. Read both sides as raw bytes — text mode translates `\r\n`→`\n` and a trailing-newline-dropping split hides a lost final newline, so a line-list comparison is not byte-for-byte: `sys.path.insert(0, "scripts")` and use `verify_blob` (`blob(base, path)`, `to_lines`, `reconstructed`) for the read-and-compare, which does not differ per change — only the reconstruction that splices your edit in does.
```

The single point mutation: `expecting no hits, and assert` → `expecting no hits (the **removed-phrase grep**), and assert`. Every other byte of the line is unchanged; the comma that followed `hits` now follows the closing parenthesis. Nothing else in `CLAUDE.md` changes.

### Anchor 2 — the ADR pointer

Replace exactly one line: `docs/adr/0001-duplicate-the-two-dev-flow-variants.md:9`, anchored by its unique substring `the residue-grep and design-conformance rules`. Its current text is:

```text
A one-sided edit to the hand-mirrored pair passes every check in CI. Changes touching it must carry their own verification — see the residue-grep and design-conformance rules in `CLAUDE.md`, both of which exist because this gap was hit in practice.
```

The single point mutation: `residue-grep` → `removed-phrase grep` (unbolded, as the surrounding "design-conformance" is). Every other byte of the line is unchanged. Nothing else in the ADR changes.

### Exact replacement text (the two plain fenced blocks — the Execute stage lifts these verbatim)

Block 0 → `CLAUDE.md`:

```
- **Always:** grep for the exact phrases the edit removes, expecting no hits (the **removed-phrase grep**), and assert that every file the edit touches is byte-for-byte its merge-base blob (nothing, for a file it creates) with exactly the intended edit applied. The other checks here prove that edit landed; only this one proves nothing else did. Read both sides as raw bytes — text mode translates `\r\n`→`\n` and a trailing-newline-dropping split hides a lost final newline, so a line-list comparison is not byte-for-byte: `sys.path.insert(0, "scripts")` and use `verify_blob` (`blob(base, path)`, `to_lines`, `reconstructed`) for the read-and-compare, which does not differ per change — only the reconstruction that splices your edit in does.
```

Block 1 → `docs/adr/0001-duplicate-the-two-dev-flow-variants.md`:

```
A one-sided edit to the hand-mirrored pair passes every check in CI. Changes touching it must carry their own verification — see the removed-phrase grep and design-conformance rules in `CLAUDE.md`, both of which exist because this gap was hit in practice.
```

These are the only two untagged (plain) triple-backtick blocks in the document, so `python3 scripts/design_blocks.py <design>` reports **shape `[1, 1]`** — block 0 the `CLAUDE.md` line, block 1 the ADR line, each one line long — and `read_blocks(DESIGN, [1, 1])` returns both for the Execute stage's conformance check. The `text`-tagged "before" blocks above and the `sh`-tagged verification block below are tagged fences and are deliberately excluded from the block shape.

## Rejected alternatives

### Name candidates

- **"the residue grep" / "residue-grep"** — used in `docs/adr/0001:9` (until this change) and in several plan docs, and it is the token #39's measurement variable itself used (`residue-grep=True`). Rejected: "residue" is a metaphor (leftover text) a step less transparent than "removed-phrase", and — decisively — the authoritative brief (issue title + owner comment) already settled on "removed-phrase grep". Coining "residue" here would contradict the very comment that commissioned the name. It also would not match the clause's own word "phrases".
- **"the removed-text grep"** — a plausible candidate. Rejected: "text" is vaguer than "phrase", and it introduces a third noun alongside the clause's existing "phrases", where "removed-phrase" reuses that exact noun and stays internally consistent with the sentence it lives in.

### Placement candidates

- **Leading label** — e.g. `**Always:** the **removed-phrase grep** — grep for the exact phrases the edit removes, expecting no hits — and assert …`. Rejected: the em-dash aside orphans the `grep … and assert …` conjunction — the sentence's subject becomes the name, leaving "the removed-phrase grep … and assert that every file …", which is ungrammatical. It also rewrites more of the line than an appositive does. The trailing bold appositive binds name to definition in place and keeps every other byte identical, which is what makes the change surgical and machine-verifiable.
- **Restructure into two named checks** (e.g. "two checks. The removed-phrase grep: …. The blob assertion: …") — Rejected as over-engineering: it rewrites the whole clause to solve a naming problem that a 30-byte insertion solves, violating "keep the rest byte-identical" and adding editorial risk for no benefit.

### Scope candidates

- **`CLAUDE.md` only, leaving the ADR on "residue-grep"** — the original draft's choice, rejected on review. The ADR line is not a historical record: it sits under `## Consequences` as a present-tense instruction that routes future work to a rule by name. Leaving it on a rejected alias is the exact "per-instance fix the next person must remember to repeat" latent regression #54 exists to end, and the demand is measured, not speculative — `residue` has exactly two shipped homes (this clause and ADR:9), so aligning both is a bounded, complete closure of the drift rather than an open-ended sweep. The swap carries no version-bump obligation (nothing under `plugins/`) and no sync obligation (the ADR is not a `check-sync.py` mirror pair), so its whole marginal cost is one word plus one file in this change's own verification.

## Assumptions (defensible defaults; none are blocking ambiguities)

- **A1 — Canonical name = "the removed-phrase grep."** Backed by the issue title, the owner's comment usage, and #39's design. Default, not a guess.
- **A2 — Scope is this one `CLAUDE.md` insertion plus the one-word ADR alignment.** No `plugins/` change, no `SKILL.md` change, no `scripts/` change, no version bump — no file under `plugins/` is touched, so `scripts/check-version-bump.py` requires none, and the ADR is not under `plugins/` and not a `check-sync.py` mirror pair, so it carries neither a bump nor a sync obligation.
- **A3 — The PR closes #54**, recording the pipeline-general question as answered-no with the 13-repo measurement as the record.
- **A4 — Anchor by content, not line number**, for both edits. The clause is line 16 at HEAD but the brief cites 15; the Execute stage matches each edit on its unique substring, so it is correct regardless of drift.

## Out of scope

- **No `plugins/` change.** The pipeline-general question is closed **answered-no** (13-repo measurement above). No bullet is added to any pipeline `SKILL.md`; nothing ships into other repos.
- **No `SKILL.md` change** of any kind — this touches only `CLAUDE.md` (this repo's own auto-loaded contributor file) and `docs/adr/0001`; no plugin `SKILL.md` is touched, so nothing new ships into model invocations in other repos.
- **No version bump** — no file under `plugins/` moves.
- **Dated `docs/superpowers/` artifacts that used "residue" are left untouched.** They are historical design/plan records, not live pointers, so aligning them would rewrite history for no navigational gain; the removed-phrase grep below is file-scoped away from them.

## Verification approach

Three checks, each already prescribed by `## Verifying a change` and applicable to this change:

1. **Removed-phrase grep — one target per file, each scoped.** Neither edit removes vocabulary wholesale, but each dissolves one contiguous string that must be gone afterward:
   - `CLAUDE.md`: the appositive splits `expecting no hits, and assert`. **File-scoped**, because that same string appears verbatim in several committed `docs/superpowers/` artifacts (the gh-32/33, gh-39, and gh-51/55 designs quote the clause), so a repo-wide grep would false-positive on history. Verified while drafting: `git grep -F 'expecting no hits, and assert' HEAD -- .` returns multiple hits, whereas `git grep -c -F 'expecting no hits, and assert' HEAD -- CLAUDE.md` returns exactly `1`.
   - ADR: the swap removes the token `residue-grep`, and with it the last shipped use of `residue`. **Scoped to exclude `docs/superpowers/`**, whose dated artifacts legitimately still say "residue". Verified while drafting: `git grep -c -i 'residue' HEAD -- . ':(exclude)docs/superpowers'` returns exactly `1` (the ADR line), so post-edit it must be `0`.

    The two Execute-stage checks are therefore:

    ```sh
    git grep -F 'expecting no hits, and assert' -- CLAUDE.md                 # after the edit, in the working tree: expect 0 (it is 1 before the edit — so 0 is non-vacuous)
    git grep -i 'residue' -- . ':(exclude)docs/superpowers'                  # after the edit, in the working tree: expect 0 (it is 1 before the edit — so 0 is non-vacuous)
    ```

2. **`verify_blob` byte-for-byte merge-base-blob assertion — both files.** `CLAUDE.md` and `docs/adr/0001-duplicate-the-two-dev-flow-variants.md` must each equal their merge-base blob with exactly their one intended line replaced — no stray edit anywhere else, read as raw bytes (`sys.path.insert(0, "scripts")`; `verify_blob` → `blob(base, path)`, `to_lines`, `reconstructed`). Each reconstruction splices its single-line replacement (block 0 for `CLAUDE.md`, block 1 for the ADR) onto the line matching that file's anchor substring; every other byte is asserted identical to the base blob. Because the design doc is a newly created file, its own `verify_blob` base is empty.

3. **`read_blocks` design-conformance check.** This design gives the two replacements as two plain fenced blocks, so `python3 scripts/design_blocks.py <design>` reports shape `[1, 1]`, and a per-change `python3` check does `sys.path.insert(0, "scripts")`, `read_blocks(DESIGN, [1, 1])`, and asserts `blocks[0][0]` appears verbatim in `CLAUDE.md` and `blocks[1][0]` verbatim in the ADR — never retyped. If the design's block shape moves, `read_blocks` exits non-zero.

### Measurements stated in this design, and the command behind each

- **13 repos / ~90 docs / zero removed-phrase-vocabulary hits** — cited from the issue #54 owner comment (2026-08-03); **not re-run here**.
- **Ten designs, three labels, one wrong count (9→10 of 10)** — cited from `docs/superpowers/specs/2026-08-02-gh-39-verification-rules-home-design.md`; **not re-run here**.
- **Clause is `CLAUDE.md:16` at HEAD; ADR pointer at `docs/adr/0001:9`** — `git grep -n -E 'removed[ -]phrase|residue|expecting no hits' HEAD` (run while drafting).
- **`residue` has exactly one shipped home (`docs/adr/0001:9`)** — `git grep -c -i 'residue' HEAD -- . ':(exclude)docs/superpowers'` returns `1` (run while drafting); post-edit it must be `0`.
- **Pre-edit `CLAUDE.md` phrase appears repo-wide but once in `CLAUDE.md`** — `git grep -F 'expecting no hits, and assert' HEAD -- .` (multiple) vs `… -- CLAUDE.md` (1) (run while drafting).
- **`CLAUDE.md` insertion is 30 bytes; the pre-edit contiguous phrase is absent post-edit** — `python3` reconstruction of the line, asserting `len(new)-len(old)==30` and `b'expecting no hits, and assert' not in new` (run while drafting).
