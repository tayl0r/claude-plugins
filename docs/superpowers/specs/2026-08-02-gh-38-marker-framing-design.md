---
dev-flow:
  slug: gh-38-marker-framing
  stops: [pre-merge]
  docs: commit
---

# gh-38: the review marker's framing and extraction

**Ruling: SHIPS**, as one replacement line in each pipeline `SKILL.md`'s **Review state** paragraph — widened on the write side (the marker is *posted* as the comment's first line, not merely *contained* somewhere in it) and corrected on the read side against the wording the issue proposes, which is measurably unimplementable: `gh pr view <pr> --json comments` exposes no comment *number* at all, only an opaque GraphQL node ID, so "the highest-numbered comment" names an ordering the pipeline's own tool cannot produce. The shipped rule orders by `createdAt` instead.

The issue argues against itself well and the no-change reading nearly holds. What defeats it is not risk — the issue is right that every mis-parse fails safe, and this document strengthens that claim rather than weakening it — but **determinism**. The Artifact Contract's opening sentence promises "every resume decision is a mechanical read", and the resume table's own header promises "each is mechanical". Marker extraction is the one predicate in the contract that no command defines, and on real inputs this pipeline produced (PR #37, PR #25) two conforming readers return different answers. A predicate that is not a function of the state is not mechanical, whichever way it errs.

## What was verified before designing

Run in this worktree against base `b4b5d1c` (`git merge-base origin/main HEAD`), which is `origin/main`'s tip.

- **The two target lines.** `plugins/dev-flow/skills/dev-flow/SKILL.md:167` and `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:161`, both the paragraph opening `**Review state.**`. Measured: `b[160].replace("dev-flow-worktree", "dev-flow") == a[166]` is **True** — the two lines are already exact substitution images, differing only inside the backticked marker string (351 vs 360 characters). One replacement text, substituted, therefore serves both.
- **File lengths:** `dev-flow` 277 lines, `dev-flow-worktree` 271. The chosen edit changes one line in each and adds none, so both counts are preserved.
- **`check-sync.py` does not cover this pair.** `MIRROR_PAIRS` in `scripts/check-sync.py` holds exactly one entry, `adversarial-review`. The pipeline pair is the **hand-mirrored** kind per `CONTEXT.md`; a one-sided edit here is caught by nothing, which is why *Success criteria* 3–6 exist. Baseline today: `check-sync: all checks passed`, exit 0.
- **Nothing outside the two `SKILL.md`s mentions the marker.** `git grep -in 'marker\|review clean' -- '*README.md' CONTEXT.md docs/adr` returns **no hits**. Within `plugins/`, `marker` occurs only in the two pipeline files. So the change is contained, and **no `CONTEXT.md` edit is implied** — see *Out of scope* for why, stated as a positive finding rather than a scope dodge.
- **The removed phrase `with the marker line` survives legitimately outside `plugins/`.** `git grep -n 'with the marker line'` returns the two target lines plus four hits in `docs/superpowers/` records (`2026-07-20-dev-flow-design.md:114`, `2026-07-24-gh-6-docs-policy-plan.md:643/649/669`). Those are dated records and are **not** to be "also fixed"; every grep below is scoped to `plugins/`.
- **PR #37's marker comment**, first lines verbatim, the real mis-parse:

  ```text
  dev-flow: review clean @ 02ffb7bcaf8ba6087cfc7577d38b979245f0cad8

  Reviewed at this SHA. No automated test suite exists in this repo; the design's eight success criteria are the verification surface and all eight are green at this head — ...
  ```

  followed by six further lines — three report paragraphs (suite results, review provenance, a sequencing note) separated by blanks; seven lines in all.
- **Full marker census, all 19 PRs.** Every issue comment on every PR, first line matched against `^dev-flow(-worktree)?: review clean @ `: **12 marker comments on 10 PRs**, all authored by `tayl0r`, all reporting `includesCreatedEdit: false`, and none of the repo's 13 issue comments containing a carriage return. Exactly one carries prose (#37). **Two PRs carry two markers each** — #14 (`1d93d696…` at `2026-07-27T18:41:57Z`, `67d0cfef…` at `2026-07-27T19:12:44Z`, 31 minutes apart) and #25 (`c6faea4…` at `2026-07-30T20:18:11Z`, `c40ae97…` at `2026-07-31T23:01:38Z`) — the ordinary result of a marker being invalidated by a push and a re-review posting a second one. **In both, the later-created comment's SHA is the one equal to that PR's final head**, independent corroboration that *most recently created* picks the marker certifying the reviewed head. This is the sub-ambiguity the issue is least confident about, and it has two measured instances — the rubric's bar for widening, not speculation.
- **Why the read predicate has to be defined, not merely implied.** With the write side pinned but "matches" left to the reader, a lenient prefix match accepts a first line carrying an *abbreviated* SHA — what a producer writing `git rev-parse --short HEAD` emits. Measured in this worktree, with `b4b5d1c` abbreviating head: `git rev-list --count b4b5d1c..HEAD` is `0`, so the trailer conjunct's `0 -eq 0` holds, and `git diff --no-renames --name-status b4b5d1c HEAD` is empty, so Marker validity's second clause is vacuously satisfied — the marker reads **valid** and routes to the **merge gate**. A strict reader rejects the same line as not a marker and routes to **PR review**. Neither answer is dishonest (the short SHA does denote head, and no misreading was found that manufactures a merge the marker fails to certify), but the two readers diverge *across the merge boundary*, which is precisely what "each is mechanical" forbids — and the producer here is a model reading this same prompt, so the slip is expected rather than adversarial. Defining the predicate makes the strict answer the only one, turning a producer slip into a loud, self-healing PR review instead of a silent merge.
- **`gh pr view --json comments` returns no comment number.** Its `id` field for those two comments is `IC_kwDORtVqi88AAAABMh6ylQ` and `IC_kwDORtVqi88AAAABMtrxHA` — opaque GraphQL node IDs. The numeric id appears only in the `url` (`#issuecomment-5148176668`) or via `gh api repos/{owner}/{repo}/issues/{n}/comments`. The two comments came back **oldest-first**, and `createdAt` is present in the same payload.
- **The two marker strings do not prefix one another.** `"dev-flow-worktree: review clean @ "` starts with `dev-flow`, but the next character is `-`, not `:`. So neither marker is a prefix or substring of the other. This matters: Branch ownership states a `<username>/<slug>` branch "may be … a feature of the sibling `dev-flow-worktree` plugin (both plugins share this pattern)", so one PR can legitimately carry markers from both variants, and a first-line exact match on a variant's own marker string correctly ignores the sibling's. Had the strings collided, a `startswith` rule would have been unsafe and the design would have had to anchor differently.
- **Version state.** `origin/main` is at `dev-flow` **2.8.0** and `dev-flow-worktree` **1.10.0**; the working tree matches. Full history of both `plugin.json` files: every version either plugin has ever shipped has a **zero patch segment** (`1.0.0`, `1.1.0`, `1.2.0`, `2.0.0/1.3.0` … `2.8.0/1.10.0`).

## Decomposition check

One issue, one concept (how a single token is framed and found), two files that are hand-mirrors of each other, one version-bump pair. Nothing here spans independent subsystems: the write side (Stage 4 posts the comment) and the read side (the resume table and merge-gate step 1 consume it) are two halves of one contract and must move together — that is in fact the argument for where the edit goes. **No split.**

## The problem, from evidence

The Artifact Contract says to "post a PR comment **with the marker line** `dev-flow: review clean @ <full-head-sha>`", and Marker validity turns on "the marker SHA equals the current head". Between those two sentences sit three unanswered questions:

1. **How is the SHA extracted** from a comment body?
2. **May the comment carry anything besides the marker?**
3. **Which comment is operative** when more than one matches?

### What each reading does to #37's comment

| Reading of "a comment with the marker line" | Verdict on #37 | What a naive extractor returns |
|---|---|---|
| body **equals** the marker | no match → "no marker" → PR review | — |
| body **starts with** the marker | match | prefix-strip of the **whole body** → `02ffb7b…\n\nReviewed at this SHA. No automated…` — **the observed failure** |
| body **contains** the marker as a substring | match | same, unless line-anchored |
| body **has a line equal to** the marker | match | correct SHA |

The fourth row is the most natural reading of the shipped words — "with the marker *line*" most plausibly means "has a line that is the marker" — and it is the reading that returns the right answer for #37. That is the no-change case's strongest fact and it is stated here at full strength, not smuggled.

It is also the reading most exposed to the collision the issue names: a line-anchored *contains* rule matches a marker that a report, a review summary, or a human comment reproduces on its own line. Nothing in the shipped text distinguishes a marker from a quotation of one.

### What actually broke, and what it cost

A reader that prefix-stripped the whole body returned SHA-plus-prose, compared unequal to head, and reported a valid marker invalid. Under the resume table that routes to **re-review** — the pipeline's most expensive operation (seed and resolver fan-out on `opus`), run against a PR that was already clean — plus an operator report that says the opposite of the truth. `Command discipline`'s "validate non-empty" guard does not catch it: the mis-parsed value is very much non-empty.

### Fail-safe, verified harder than the issue verified it

The issue claims it could not construct a non-adversarial path to a false *valid*. That holds, and the same is true of the operative-comment question, which the issue does not analyse:

- **Clause 1 (marker SHA equals head).** If *any* matching comment carries a SHA equal to head, the certification it makes — "reviewed and suite-green at this exact SHA" — is true of head regardless of which comment carried it. So choosing the wrong comment cannot manufacture a false valid here; it can only manufacture a false *invalid* (choosing an older marker whose SHA is stale).
- **Clause 2 (the proven strip).** The range is `<marker-sha>..HEAD`. Choosing an *older* marker widens the range, which can only add trailer-less commits or non-`D` diff entries — strictly harder to satisfy. Choosing the newest marker is both the permissive direction *and* the correct one, since the newest marker is the one that certifies the reviewed head.

So every error mode routes to re-review. **Severity is genuinely low and this document does not inflate it.** The argument for acting has to come from somewhere else, and it does.

## The case for NO CHANGE, at full strength

**N1. The spec already names the unit, and the reader ignored it.** It says marker *line*. A line-oriented reader — `split("\n")` and look at lines, not at the body as one string — is invited by the words on the page, is trivial, and returns the right answer for #37 and for every marker this repo has ever posted. What broke was a reader doing something the spec never suggested: prefix-stripping a whole multi-line body. "Readers should be line-oriented; the reader was the bug" is an honest close.

**N2. The consequence is bounded and provably safe** — established above, in more directions than the issue checked. No merge is ever unsafe. The cost is a redundant review and a misleading line of operator output.

**N3. Prompt budget is the real currency.** This text ships into every model invocation of a 277-line skill, inside the Artifact Contract, already the file's densest section. The chosen edit adds 561 characters to a 351-character line. Every sentence added to a prompt competes for attention with every other sentence, and the rubric's **"Every change must earn its place; if the fix is worse than the wart, leave it"** bites hardest exactly where the artifact *is* the prompt.

**N4. Rarity.** Across all 19 PRs in this repo's history there are 12 marker comments; exactly one carried prose (#37), and **two** PRs carried two markers each (#14, #25). The rubric says to **"skip super-rare edge cases … unless the fix is essentially free"**, and 561 characters of prompt is not free.

**N5. The issue's own proposed wording is wrong**, in a way only measurement reveals (see *Options*, (c)). That is evidence the area is subtler than "about one sentence", and a hasty edit here risks shipping a rule *worse* than silence — a rule that names an ordering the tool cannot produce sends the next reader to `gh api` for a numeric id they did not need, or to sorting opaque node IDs lexicographically, which happens to work today by accident of encoding and is not a contract.

## Rebuttal, and why it ships anyway

**R1 against N1 — "line" fixes the unit, not the position or the match.** A reader told to find "the marker line" inside a 12-line comment must still decide *which* line and *how* to match it. #37's reader picked one bad answer; "grep the body for the marker" is another, and that one is **worse than the failure actually observed**, because it matches a quotation. The shipped words exclude none of the four readings in the table above — a comment consisting solely of the marker satisfies "with the marker line" too, so even *equals* survives. N1 is right that a line-oriented reader is invited; it is wrong that the invitation is an instruction.

**R2 against N2 — fail-safe is not free, and the cost landed on the first PR that exercised it.** A full adversarial re-review of an already-clean PR is the most expensive thing this pipeline does. More importantly, safety is the wrong axis: nothing in this design is justified by risk.

**R3 — the argument that carries the ruling: "mechanical" is a promise the contract makes about itself, and this predicate breaks it.** Three places state it verbatim, in both files:

- `:66` — "every resume decision is a **mechanical read** of one of those two places."
- `:181` — "**Resume table** (checks run top-to-bottom, first match wins; **each is mechanical**; …)"
- `:275` — "**Idempotent resume:** guaranteed by the Artifact Contract — every resume decision is a **mechanical read** of the branch tip or the PR."

A mechanical read is one where two conforming readers, given the same state, return the same answer. On #37 they demonstrably do not, and on #25 two *line-oriented* readers — first match versus last match — return different SHAs. This argument is independent of severity, independent of blast radius, and unanswerable by "the reader was the bug": the reader can only be wrong if there is a right answer, and the contract does not supply one. It is not, however, the same *kind* of fact as #29's decisive one — see option (a). The self-contradiction is a measured property of the text; the choice to repair it by defining the predicate, rather than by deleting the three "mechanical" promises that idempotent resume rests on, is a judgment about what the contract is for. One-sided, but a judgment, and this document does not dress it as arithmetic.

**R4 — the sibling asymmetry proves this is an omission, not a deliberate silence.** The very parenthetical that promises "each is mechanical" also supplies the tie-break for the *other* multi-valued PR read: *"latest PR" = the highest-numbered result of `gh pr list --head <username>/<slug> --state all`*. The contract already knew that "which of several" needs an answer, wrote one for PRs, and did not write one for comments. Adding it is not new policy; it is the missing instance of a rule this section already writes for its sibling — and this design supplies the reason the same words could not simply be copied.

**R5 against N5 — "the issue's wording is wrong" argues for designing the sentence, not for skipping it.** Catching that is the value a design pass exists to add. Weighing it as a reason not to act converts every subtle problem into an unfixable one.

**R6 — rubric, on the widening.** *"Value simplicity; widen the lens only against concrete demand (planned siblings, 2+ instances), never speculation."* Two instances are measured: #37 (extraction) and #25 (operative comment). *"Prefer correct-by-default seams over designs where each caller must remember a flag, ordering, or manual step"* is what puts the text where it goes — see *Where the edit goes*.

**Ruling: SHIPS.**

## Options considered

**(a) No change; record the ruling.** The precedent form (`2026-08-02-gh-28-29-review-prose-design.md`, *Issue #29*). **Rejected** on R3: unlike #29, where the decisive fact was that a cross-reference could not resolve for its only reader — a property of the text that no amount of care would fix — here the shipped text simply does not answer a question every consumer must answer, and the section's own self-description says it does. #29's ruling protected a legitimate divergence; there is no legitimate divergence to protect here, only an absent rule.

**(b) One replacement line in **Review state**, both files.** **CHOSEN.** Text and anchors in *The edit*.

**(c) The issue's candidate wording, verbatim** — "the marker is the **first line** of its comment; the comment may carry anything after it; the operative marker is the **highest-numbered comment whose first line matches**." **Rejected on its third clause, measured.** `gh pr view <pr> --json comments` — the reader the rest of the contract implies, and the one that reports `body` — returns `id` as an opaque GraphQL node ID (`IC_kwDORtVqi88AAAABMtrxHA`), not a number. There *is* a numeric comment id, but only via `gh api repos/{owner}/{repo}/issues/{n}/comments` or by scraping `#issuecomment-…` out of the `url`. So the clause as written either sends the reader to a second API for an ordering it does not need, or invites sorting opaque node IDs — which happens to sort correctly today because the encoding is fixed-width big-endian, and is not a contract. The clause is also weaker than necessary even where it works: comment ids are globally monotonic, so "highest-numbered" and "most recently created" coincide, but only the latter is readable from the payload the pipeline already has. The first two clauses are adopted; the third is replaced by *most recently created*, with the ordering source named. This is precisely the correction the issue could not make from the outside, and it is why (a) is not the cheap-and-equal outcome it looks like.

**(d) A new named paragraph, `**Marker framing.**`, between **Review state** and **Marker validity**.** Tempting: the Artifact Contract's bold run-ins are its index, and named paragraphs get referenced by name (`Marker validity` is cited from four places). **Rejected.** The framing rule is a contract *between* the writer of the marker and its reader; separating the sentence that says "post it as the first line" from the sentence that says "read the first line" is exactly the seam at which they will drift, and nothing would catch it. Keeping both in one paragraph is the correct-by-default arrangement. Secondarily, it would add two lines and shift every subsequent line number in both files, weakening the changed-line-set proof (criterion 6) for no design gain, and three sibling paragraphs where two are about one token over-indexes the marker relative to `Slug`, `Branch identity`, and `Docs policy`.

**(e) Pin an exact extraction command** — a `gh … --jq …` pipeline in a fenced `sh` block, the way `Marker validity`'s trailer conjunct is pinned. **Rejected.** That block earns its fence on a failure *class*, not on subtlety: an empty `<marker-sha>` collapses the range to `HEAD..HEAD`, where `0 -eq 0` returns **valid** — the one direction that reaches a merge. That is the line worth a fenced block. It is *not* true that extraction has no residual trap: "the operative marker, when several match, is the latest" has to be read as filter-then-last, and a reader who takes the PR's last comment outright gets a wrong answer. But the shipped text names the filtered set twice ("when several match", "so it is the last match"), the residual is a misreading of unambiguous prose rather than an ambiguity in it, and it fails to a re-review. Pinning a jq incantation to close it would freeze a `gh` output shape that is version-dependent — `address-pr-feedback/SKILL.md:42` already documents that `gh pr view --json comments` and `gh api` disagree on field names. The chosen text names the command and the two properties a reader needs (oldest-first, `id` is not a number) without pinning a pipeline.

**(f) Change the carrier so framing is unambiguous by construction** — an HTML-comment sentinel (`<!-- dev-flow: review clean @ <sha> -->`), a fenced block, or a git note / ref instead of a PR comment. **Rejected on three counts.** It is a format migration, not a clarification: every marker on every open PR stops matching, and the contract would need a compatibility window it currently has no vocabulary for. It removes the marker from human view, which the issue explicitly values and which the existing parenthetical — "(A label can't carry the SHA and goes silently stale — rejected.)" — shows was already weighed once in favour of a visible, SHA-carrying comment. And it does not settle question 3 at all: two sentinels are as possible as two comments. A carrier change would need its own issue and its own evidence; nothing in #38 supplies either.

**(g) Fix it outside the spec** — a `scripts/` helper that extracts the marker, or a `CLAUDE.md` rule. **Rejected on merits and forbidden by scope.** On merits: this pipeline ships as a prompt into arbitrary repositories, so a script living in *this* repo's `scripts/` is unavailable to every consumer of the plugin — it would fix this repo's next run and no one else's. On scope: `scripts/` and `CLAUDE.md` are outside this change's authorized file set (see *Out of scope*), and are recorded here as rejected on substance so a later reader does not mistake exclusion for oversight.

## Where the edit goes

**`Review state`, one replacement line per file** — `dev-flow` `:167`, `dev-flow-worktree` `:161`.

That paragraph already owns both halves of the contract: it is where the marker is minted ("post a PR comment with the marker line …") and where its consumption is routed ("Detection: marker **valid** -> merge gate; …"). Putting the framing between those two sentences means a future edit to how the marker is written sits in the same line as the rule for how it is read — the rubric's *"put the fix at the shared seam so current and future members inherit it"*, applied to prose. `Marker validity` immediately below is untouched and correctly so: it answers "is this SHA still good", which is a different question from "which SHA, from where".

No line is added or removed. `dev-flow` stays **277** lines and `dev-flow-worktree` stays **271**, `Marker validity` stays at `:169`/`:163`, and every line number cited elsewhere in this document remains valid after the edit.

## The edit

Each block below is the **complete final line** as it must read in its file. There is no leading whitespace. Copy these bytes; do not retype them. **Anyone rewriting this document — the design review that precedes implementation included — must leave these two fences plain (no language tag), one line each, and must not add a plain fence anywhere else in this document.** Criterion 4 reads them back from disk by position among the plain fences; `read_blocks` exits non-zero rather than misroute if that shape moves, so a violation halts the implementation instead of corrupting it.

**Anchor:** each replaces the single line whose current text begins `**Review state.** After Stage 4's review has committed its fixes` — line **167** in `plugins/dev-flow/skills/dev-flow/SKILL.md`, line **161** in `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`. Match on that text, not on the number, and halt if the current line differs from the pre-edit text quoted in *What was verified* (A1).

### `plugins/dev-flow/skills/dev-flow/SKILL.md`, line 167

```
**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment whose **first line** is exactly the marker `dev-flow: review clean @ <full-head-sha>` — the SHA in full, nothing else on that line — with any report prose on the lines below. A comment is a marker **exactly when its first line has that form**; read the SHA from that line, never from a scan of the body, which also matches a report or comment that merely *quotes* a marker. The **operative** marker, when several match, is the latest by `createdAt` — `gh pr view <pr> --json comments` carries it and lists comments oldest-first, so it is the last match; never order by `id`, an opaque node ID there, not a number like a PR's. Detection: marker **valid** -> merge gate; marker present but **invalid** -> re-review; no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)
```

### `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`, line 161

```
**Review state.** After Stage 4's review has committed its fixes and the stage has pushed, post a PR comment whose **first line** is exactly the marker `dev-flow-worktree: review clean @ <full-head-sha>` — the SHA in full, nothing else on that line — with any report prose on the lines below. A comment is a marker **exactly when its first line has that form**; read the SHA from that line, never from a scan of the body, which also matches a report or comment that merely *quotes* a marker. The **operative** marker, when several match, is the latest by `createdAt` — `gh pr view <pr> --json comments` carries it and lists comments oldest-first, so it is the last match; never order by `id`, an opaque node ID there, not a number like a PR's. Detection: marker **valid** -> merge gate; marker present but **invalid** -> re-review; no marker -> PR review. (A label can't carry the SHA and goes silently stale — rejected.)
```

The two differ at exactly one span — `dev-flow:` versus `dev-flow-worktree:` inside the backticked marker — and the token `dev-flow` occurs exactly once in the first block, `dev-flow-worktree` exactly once in the second. Verified: applying `dev-flow-worktree` → `dev-flow` to the second block yields the first, byte for byte. Criterion 5 re-checks this from the blocks as read off this document.

### What each clause settles

| Clause | Question | Effect |
|---|---|---|
| "whose **first line** is exactly the marker … the SHA in full, nothing else on that line" | 1, write side | Pins the producer, giving the reader a form to be measured against — including that the SHA is unabbreviated. |
| "with any report prose on the lines below" | 2 | #37's comment is explicitly legal. The prose is genuinely useful to a human reading the PR and is not being taken away. |
| "A comment is a marker **exactly when its first line has that form**" | 1 + 2, read side | Binds the read predicate to the write form in both directions. Every malformed first line — abbreviated SHA, trailing content, blank body, leading blank line, a quoted marker — is *not* a marker: one answer for every conforming reader, and the safe one (no marker -> PR review). This is what makes "mechanical" true rather than asserted; without it a lenient reader routes an abbreviated-SHA marker to the merge gate while a strict one routes it to PR review. |
| "read the SHA from that line, never from a scan of the body" | 1, read side | Kills the observed failure (whole-body prefix strip) and the more dangerous line-anchored *contains* reading. |
| "The **operative** marker, when several match, is the latest by `createdAt`" | 3 | Makes the predicate a function of PR state. Also the semantically correct choice: the newest marker certifies the reviewed head, which is what `Marker validity`'s strip clause needs as its range start — corroborated on both real multi-marker PRs, #14 and #25, where the later comment's SHA is the one equal to final head. |
| "`gh pr view <pr> --json comments` carries it and lists comments oldest-first … never order by `id`" | 3, mechanics | Names the ordering key inside the payload the pipeline already reads, and closes the trap the resume table's neighbouring "highest-numbered result" idiom actively sets. |

### Removed phrase — grep expecting zero hits

Scope to `plugins/`. Repo-wide the phrase still hits, correctly, in four `docs/superpowers/` records (a prior design and a prior plan); those are dated records and are not to be touched.

```sh
git grep -n 'with the marker line' -- plugins/    # expect: no output, exit 1
```

## Version bumps

Text in these files ships into every model invocation, so this is a behaviour change under `CLAUDE.md`'s bump rule, and the install cache is version-keyed — an edit at an unchanged version is never picked up on re-sync.

- `plugins/dev-flow/.claude-plugin/plugin.json`: **2.8.0 → 2.9.0**
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json`: **1.10.0 → 1.11.0**

**Why minor and not patch.** Same reasoning as the immediately preceding change, and unchanged by it: `CLAUDE.md` requires a bump "on any behavior change" and says nothing about which segment; a patch bump busts the version-keyed cache exactly as well. Minor is chosen because **no version either plugin has ever shipped has a nonzero patch segment** (verified across the full history of both `plugin.json` files), and because establishing a minor-vs-patch convention is a repo-policy decision whose home is `CLAUDE.md` — outside this change's file set.

**Why criterion 7 compares against `origin/main` and not only against a literal.** This bit a pipeline today. PR #37 was designed against versions `2.7.0`/`1.9.0`; PRs #35 and #36 merged while it was in flight and took exactly those numbers. Merging `origin/main` into the branch **auto-resolved with no conflict** — both sides moved the same line in the same direction, so git saw nothing to ask about — which would have shipped the change's text at an already-published version the cache would never pick up. `check-sync.py` does not see it. `claude plugin validate .` does not see it. A criterion that only asserts `"version": "2.9.0"` does not see it either. Only a comparison against the *published* version does, and only if it is re-run **after** the last merge or rebase, immediately before the halt.

## Success criteria

Every item is mechanically checkable. `BASE` = `git -C <working-dir> merge-base origin/main HEAD` throughout — never a hardcoded SHA, so it stays correct if `main` advances or the branch is rebased. Criteria **1–3 and 8 are shell**; **criteria 4–7 are one Python program**, run top-to-bottom in a single interpreter once the edit and the version bumps are in the working tree. The block below is that program's preamble — the only place `ROOT` is substituted, the only place `BASE` is computed for it, and the sole definition of every helper the four criteria share. Nothing below re-defines them, and no criterion below is runnable on its own.

```python
import json, subprocess, sys

ROOT = "<working-dir, absolute>"   # the one substitution the implementation supplies
sys.path.insert(0, f"{ROOT}/scripts")
from design_blocks import read_blocks

DESIGN = "docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md"
DF = "plugins/dev-flow/skills/dev-flow/SKILL.md"
WT = "plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md"
JSON_DF = "plugins/dev-flow/.claude-plugin/plugin.json"
JSON_WT = "plugins/dev-flow-worktree/.claude-plugin/plugin.json"
TARGETS = [(DF, 167, 277), (WT, 161, 271)]      # path, 1-based anchor line, total lines
(_, DF_LINE, _), (_, WT_LINE, _) = TARGETS      # the only copy of the two line numbers

def run(*args):                   # every git call: same repo, non-zero fails loud
    return subprocess.run(["git", "-C", ROOT, *args],
                          capture_output=True, text=True, check=True).stdout

def split_lines(text):            # check-sync.py's rule; agrees with `wc -l`
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out

def blob(path, rev):              # a file's bytes as of <rev>, never the working tree
    return run("show", f"{rev}:{path}")

def here(path):                   # a file's bytes as they stand now
    return open(f"{ROOT}/{path}", encoding="utf-8").read()

BASE = run("merge-base", "origin/main", "HEAD").strip()   # computed, never pasted
old_df, old_wt = split_lines(blob(DF, BASE)), split_lines(blob(WT, BASE))
new_df, new_wt = split_lines(here(DF)), split_lines(here(WT))
```

Paths are repo-relative throughout — `git show <rev>:<path>` resolves them from the repo root and `here` joins them onto `ROOT` — so nothing here depends on the current directory, the `scripts` import included.

1. `python3 scripts/check-sync.py` exits **0** and reports `check-sync: all checks passed`, with the mirror-pair line unchanged (`mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`). This change touches neither member of that pair; the criterion exists to prove it did not perturb them.
2. `claude plugin validate .` exits **0** with exactly **8** `No author information provided` warnings and no errors.
3. **Removed phrase — the check outside the pair.** `git grep -n 'with the marker line' -- plugins/` → no output, exit 1. (Unscoped it still hits four `docs/superpowers/` records, by design; see *Removed phrase*.)
4. **Design-block conformance — the second check outside the pair.** Re-read the two fenced blocks in *The edit* **from this design document on disk, never retyped**, and assert each is present verbatim in its target file at its anchor line and nowhere else:

   ```python
   blocks = read_blocks(f"{ROOT}/{DESIGN}", [1, 1])   # shape guards the indexing
   for (path, lineno, total), block in zip(TARGETS, blocks):
       assert len(block) == 1, (path, len(block))
       lines = split_lines(here(path))
       assert len(lines) == total, (path, len(lines), total)
       assert lines[lineno - 1] == block[0], (path, lineno)
       assert lines.count(block[0]) == 1, (path, "block text is not unique")
   print("design blocks ok")
   ```

   The `[1, 1]` shape is this document's plain-fence shape: exactly the two single-line blocks in *The edit*. Every other fence in this document carries a language tag (`text`, `sh`, `python`) and is therefore invisible to `read_blocks`. The fence discipline that keeps this true is stated in *The edit*, where a rewriter of those blocks will see it. Reading from disk buys "never retyped", not "the spec is immutable"; `read_blocks` exits non-zero rather than misroute if the shape moved. Confirm the shape first with `python3 scripts/design_blocks.py docs/superpowers/specs/2026-08-02-gh-38-marker-framing-design.md`.

5. **Substitution-image proof — the check that the hand-mirror actually mirrored.** Computed from the blocks criterion 4 read and from the files, both **after** the edit and **at `BASE`**:

   ```python
   b0, b1 = blocks[0][0], blocks[1][0]                 # the blocks criterion 4 read
   assert b1.replace("dev-flow-worktree", "dev-flow") == b0        # the two design blocks
   assert b0.count("dev-flow") == 1 and b1.count("dev-flow-worktree") == 1
   # the same correspondence, in the files, after the edit:
   assert new_wt[WT_LINE - 1].replace("dev-flow-worktree", "dev-flow") == new_df[DF_LINE - 1]
   # and it is not newly created — it held at BASE too:
   assert old_wt[WT_LINE - 1].replace("dev-flow-worktree", "dev-flow") == old_df[DF_LINE - 1]
   print("substitution image ok")
   ```

   This is the criterion that a one-sided edit fails: an edit applied to only one file leaves the two lines non-corresponding, and `check-sync.py` — which does not know this pair exists — would still pass. The first assertion is the one criterion 4 cannot make: criterion 4 would accept two design blocks that were never mirrors of each other, and this catches a design whose two blocks drifted before either reached a file.

6. **Changed-line set — nothing outside the intended lines moved.** Evaluate after committing, when the working tree equals `HEAD` (the reader works on the working tree too, so it is also runnable before the commit exists). Compare each of the four non-doc files against its `BASE` blob by line index:

   ```python
   def changed(path):                # 1-based line numbers whose text differs from BASE
       old = split_lines(blob(path, BASE))
       new = split_lines(here(path))
       assert len(old) == len(new), (path, len(old), len(new))
       return {i + 1 for i, (a, b) in enumerate(zip(old, new)) if a != b}

   assert changed(DF) == {DF_LINE}, (DF, changed(DF))
   assert changed(WT) == {WT_LINE}, (WT, changed(WT))
   for path in (JSON_DF, JSON_WT):
       moved = changed(path)
       assert len(moved) == 1, (path, moved)
       assert '"version"' in split_lines(here(path))[next(iter(moved)) - 1], path
   print("changed-line set ok")
   ```

   Each `plugin.json` is pinned to *exactly one* changed line containing `"version"`, with the line **number** deliberately unpinned — line position is not a stable property of a JSON file. The value is criterion 7's business. No hunk headers are parsed: the comparison is by line index, so the result does not depend on diff-algorithm choices, and a stray added or deleted line trips the `len(old) == len(new)` assert instead of silently shifting the set. Together with criterion 4 this pins both `SKILL.md`s completely: every line is either byte-identical to `BASE` or the one block quoted in *The edit*. Two things follow as corollaries and get no criterion of their own — the files are still 277 and 271 lines, and `Marker validity` at `:169`/`:163` is untouched in both.

7. **Versions — strictly greater than published. Two runs, both required.**

   ```python
   WANT = {JSON_DF: (2, 9, 0), JSON_WT: (1, 11, 0)}   # the designed floor, not an equality
   def ver(text):
       return tuple(int(p) for p in json.loads(text)["version"].split("."))
   run("fetch", "origin", "main")     # refreshes refs/remotes/origin/main
   for path, want in WANT.items():
       mine = ver(here(path))
       published = ver(blob(path, "origin/main"))
       assert mine >= want, (path, "below the designed version", mine, want)
       assert mine > published, (path, "not ahead of origin/main", mine, published)
   print("versions ok")
   ```

   **7a — at implementation**, with both bumps in the working tree. **7b — immediately before the pipeline halts at `pre-merge`**, after the last merge or rebase of `origin/main` into the branch and after re-running criterion 6. Neither run substitutes for the other and a criteria pass reported without 7b is incomplete: 7b is the one that matters, because a concurrent PR that lands `2.9.0`/`1.11.0` first auto-resolves into this branch with **no conflict**, and this is the only check in the entire set that notices. `git fetch origin main` updates `refs/remotes/origin/main` under this repo's standard `+refs/heads/*:refs/remotes/origin/*` refspec, so `blob(path, "origin/main")` resolves against the tip just fetched; `run`'s `check=True` means a failed fetch halts rather than silently comparing against a stale ref. On failure, re-target both versions upward and re-run criteria 6 and 7 — `WANT` is a **floor**, not an equality, precisely so the criterion stays green through the remediation it prescribes.

8. **File scope.** `git diff --stat $BASE..HEAD` touches only: the two pipeline `SKILL.md`s, the two `plugin.json`s, and paths under `docs/superpowers/` (this design and its plan). Any other path — in particular `CONTEXT.md`, `CLAUDE.md`, or anything under `scripts/` — is a scope violation and a blocker, not a fix to apply.

## Out of scope

Hard-excluded. A proposal touching any of these is a blocker, not a design.

- **`CONTEXT.md`** — untouched, and **no edit is implied**, which is a finding rather than a scope dodge. The glossary has no **Marker** entry today and this change introduces no new name: `marker`, `valid`, and `invalid` are already the files' established terms, and `operative` and `framing` carry their ordinary-English senses, which the glossary-conformance angle's own reportability rule excludes from candidacy ("The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate"). Whether **Marker** *deserves* an entry is a separate, defensible question, recorded as a follow-up (**A6**) rather than answered here. `CONTEXT.md` is outside this change's authorized file set in any case, and concurrent agents own it.
- **`CLAUDE.md`** and **`scripts/`** — outside the authorized file set, owned by concurrent agents. Option (g) rejects a script-based fix on substance as well: this pipeline ships as a prompt into arbitrary repositories, so a helper in *this* repo's `scripts/` would fix nothing for any other consumer.
- **`Marker validity`** (`:169`/`:163`) — answers "is this SHA still good", which the framing rule does not touch. Its `<marker-sha>` input becomes better-defined by this change; its text does not need to change to say so.
- **`dev-flow-worktree/…/SKILL.md:155`'s bare mention** of "the `review clean` marker-SHA read". Deliberately left alone: `dev-flow` has no counterpart line (it has no worktree-entry step), so editing it would break the substitution-image property that criterion 5 proves, in exchange for a cross-reference the reader can already follow. Left as-is, not deferred.
- **Author scoping on the marker comment.** Rejected on the merits, not omitted. Issue #38 scopes it out explicitly ("forgery, not accident"); the pre-existing text has the identical exposure, so this change neither creates nor widens it; and, measured, the discriminator does not discriminate — all 13 issue comments in this repo's history, the 12 markers among them, are authored by `tayl0r`, the same identity a human comment carries. A rule "count only comments the pipeline authored" would filter nothing in the configuration that actually exists, at the cost of a clause in the file's densest paragraph. A real defence against forgery needs a different carrier (signed, or bot-scoped) — option (f)'s territory, with its own issue and its own evidence.
- **The marker's carrier** — HTML-comment sentinel, fenced block, git note, git ref. Rejected on the merits in option (f); a carrier change needs its own issue and its own evidence.
- **The two plugin `README.md`s** and `docs/adr/` — verified to contain no mention of the marker at all.
- **Every pre-existing file under `docs/superpowers/`** — prior records, four of which legitimately contain the removed phrase.

## Assumptions

- **A1.** Line numbers **167** (`dev-flow`) and **161** (`dev-flow-worktree`) are correct as of base `b4b5d1c`, and the two lines are exact substitution images of each other — both verified mechanically. The implementation matches on **text**, not line number, and halts if a target line's current text differs from the pre-edit text quoted in *What was verified*.
- **A2.** `gh pr view <pr> --json comments` lists comments **oldest-first**. Verified on both multi-marker PRs — #14 and #25 each returned their two marker comments in ascending `createdAt` order — and consistent with GitHub's list-comments default sort. The shipped text does not rest on it: `createdAt` is the stated ordering key, and list order is named only as the convenience that makes "the last match" cheap, so a reader remains correct if list order ever changes.
- **A3.** Comment `id` in that payload is an opaque GraphQL node ID, not a number — verified (`IC_kwDORtVqi88AAAABMtrxHA`). The numeric id exists only via `gh api repos/{owner}/{repo}/issues/{n}/comments` or the `url` fragment. The shipped text tells the reader not to order by it; it does not forbid using the REST endpoint, which also returns comments oldest-first with `created_at`.
- **A4.** The two marker strings do not prefix one another (`dev-flow-worktree:` diverges from `dev-flow:` at the character after `dev-flow`), so a first-line exact match on one variant's marker cannot match the other's — verified. This is what makes the rule safe on a branch that both plugin variants have touched, a case Branch ownership explicitly contemplates.
- **A5.** `claude plugin validate .` emitting exactly 8 `No author information provided` warnings and exiting 0 is the expected pass state, per `CLAUDE.md`. No test framework exists in this repo; the *Success criteria* are the whole verification surface.
- **A6.** One question this design identifies and defers is recorded as a follow-up GitHub issue rather than decided here: **whether `CONTEXT.md` should carry a `Marker` glossary entry** — the term is load-bearing across both pipeline files and across three separate paragraphs (`Review state`, `Marker validity`, merge-gate step 1), and it now carries a framing rule as well, which is the shape of thing the glossary exists to fix in one place. It is deferred because `CONTEXT.md` is outside this change's file set and is concurrently owned, and because adding a glossary entry carries a standing cost (every entry is grepped over every design and plan artifact forever). Filing is the pipeline's integration step, not part of the implementation; the filer first checks that no equivalent open issue exists.
- **A7.** A second question is deferred the same way: **should the marker be posted, and read, with a stable machine frame rather than a first line** — option (f). This design rejects it for #38 because it is a format migration with a compatibility window, not a clarification, and #38 supplies no evidence for one. If a future change wants it, the framing rule shipped here is what makes the migration statable ("the first line was the frame; the frame is now X"). Recorded, not filed — there is no measured problem behind it today, and filing an issue with no evidence is noise.
- **A8.** Issue #38 closes on merge, with *The edit* and this document's ruling as the closing reference.
- **A9. Degenerate first lines are decided by the predicate, not by extra clauses.** "A comment is a marker exactly when its first line has that form" settles every one: an empty or whitespace-only body, a leading blank line, a case variant, a trailing space or `\r`, and extra content after the SHA are all *not* that form, so they are not markers — one answer, reached by every conforming reader, and it is the safe one (no marker -> PR review). No trimming or normalisation clause is added: it would spend prompt text in the file's densest paragraph being *lenient* about inputs no conforming producer emits, and none of the 13 issue comments in this repo's history contains a carriage return. `createdAt` rather than `updatedAt` is deliberate: a marker certifies a review that happened at a moment, and editing a comment afterwards re-certifies nothing. All 12 markers report `includesCreatedEdit: false`, so no measured case turns on it; an edit that changes an older marker's SHA either supplies a stale one — which widens the strip range and fails safe — or types head's own, which is the forgery boundary #38 scopes out.

## Spec self-review

- **Placeholders / TBDs:** none. Both replacement lines are given in full, both version numbers are stated, every grep and every check is given as runnable code with its expected result. `<working-dir, absolute>` in the preamble block is the one substitution the implementation supplies, flagged as such at the top of *Success criteria*.
- **Internal consistency:** each replacement block is its target's current line with one substitution applied — `post a PR comment with the marker line ` \<marker\> `. Detection:` → `post a PR comment whose **first line** is exactly the marker ` \<marker\> ` — … Detection:` — and every other byte carried over unchanged, including the closing parenthetical. Measured, not eyeballed: both blocks were built by transforming the current lines and re-checked for the substitution-image property, the token counts, and the preserved head and tail. Criterion 4 asserts those exact bytes land in both files; criterion 6 asserts nothing else moved. The line counts asserted in criterion 4 (277 / 271) match *What was verified* and are consistent with criterion 6's `len(old) == len(new)`.
- **Scope:** the authorized file set is the two pipeline `SKILL.md`s, the two `plugin.json`s, this document, and its plan. Criterion 8 checks it by file; criterion 6 checks it by line. `CONTEXT.md`, `CLAUDE.md`, and `scripts/` are forbidden and — verified, not assumed — not needed: nothing outside `plugins/` mentions the marker, and the change coins no new term.
- **Ambiguity:** two places a fresh implementer could go wrong, both called out at the point of use. (i) **Grep scope** — `with the marker line` legitimately survives in four `docs/superpowers/` records; every grep is scoped to `plugins/`. (ii) **Fence discipline in this document** — criterion 4 indexes off the plain-fence shape `[1, 1]`, so an untagged fence added anywhere by a later rewrite misroutes the check; `read_blocks` exits non-zero rather than silently misroute, and the requirement is stated in *The edit*, beside the two fences it governs, where a rewriter of them will see it.
- **Applying the review's own passes to this document.** *Terminology collision and drift*, over the six names `CONTEXT.md` marks as ones to avoid (`finder`, `first-pass reviewer`, `group agent`, `judge`, `arbiter`, `boundary`): none occurs anywhere in this document outside this sentence, which is mention rather than use — in particular *first line* is not drift toward `first-pass reviewer`, since drift counts a hit only where a name names the very concept its entry defines, and *first line* names no reviewer, let alone a **Seed**. *Glossary conformance* over the diff this change produces: the two added lines introduce no term the glossary defines and no avoided synonym; `marker`, `valid`, and `invalid` are the files' pre-existing vocabulary, and `operative`, `framing`, and `first line` carry their ordinary-English senses. Grepped, not assumed, and pinned to base `b4b5d1c` so the result stays reproducible after merge — at that base exactly one of the three greps is non-empty: `git grep -n -w 'operative' b4b5d1c -- ':!docs/superpowers'`, and the same grep for `framing`, are both **empty, exit 1**, while **`first line` does hit**, exactly twice — `plugins/dev-flow/skills/adversarial-review/SKILL.md:18` and its `dev-flow-worktree` twin require a reviewer to state its model "as the first line of its report" and halt on "a missing or mismatched first line". (Re-run **unpinned** against the merged tree, the `operative` and `first line` greps additionally return this change's own two `Review state` lines — the coining itself, tautologically, not a pre-existing use for it to collide with; the pin is what excludes them. `b4b5d1c` is hardcoded here deliberately, unlike *Success criteria*'s computed `BASE`: this records a measurement taken at a moment, not a check that has to survive a rebase.) **Ruled not a collision, and recorded here so the one non-empty grep is not re-litigated.** Collision "applies only to words the artifact introduces or adopts as the name of a concept", and neither text does: both carry the single ordinary-English sense — the line of a text that comes first — differing only in the text it applies to, a reviewer's report there and a PR comment here. One sense over two objects is not two senses over one word, and the pass's own reportability rule — *"The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate"* — excludes both sides. What this change names is the **marker**; *first line* is the position the marker occupies, and *a first-line read* is no more a coined name than the *substring scan of a body* it is contrasted with. **Substitution image**, used as a property name throughout this document, is clean for the pass's other reason — *"never to a word the artifact uses in the sense the repo already has"* — being exactly the relation `CONTEXT.md`'s **Mirror pair** entry defines. **No finding** on either.
