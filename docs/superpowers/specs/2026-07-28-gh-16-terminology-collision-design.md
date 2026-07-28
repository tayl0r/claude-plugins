---
dev-flow:
  slug: gh-16-terminology-collision
  stops: [pre-merge]
  docs: commit
---

# gh-16: terminology collisions are invisible to stage reviews

## Goal

Close issue #16 with one trigger-gated pass on `adversarial-review`'s **design and plan correctness seed**, so a design that adopts a word the repo already uses for something else is reported as a finding instead of shipping. The pass reads the repo's domain glossary first and greps for what the glossary does not settle, because two of the three known collisions were against prose no glossary covered. It is findings-only and read-only: it never renames anything, never writes `CONTEXT.md`, and never proposes creating one. Nothing lands in the design rubric, the `/simplify` angles, the resolver tier, or `diff` mode.

## The evidence, restated

Three real instances, all shipped:

| Term | Artifact's sense | Colliding sense | Where the collision lived |
|---|---|---|---|
| `seam` | code-level, from `codebase-design` | protocol-level (`Step-0 seam`, "user-directed seams") | pipeline `SKILL.md` prose |
| `family` | the plugin family the two dev-flow variants share | model family (`family match`, `cross-family`) | `adversarial-review` `SKILL.md` prose |
| `angle` / `pass` | used interchangeably | two different things: a lens *inside* a seed vs. a whole check | the artifact itself |

The `seam` instance is the control. gh-7's design went through a full design-stage review — 2 `sonnet` seeds, 3 `opus` resolvers, ~484k tokens — and all five missed it. A `/grill-with-docs` pass on the same document immediately afterwards found it, along with `angle`/`pass`.

**Why the existing seeds miss all three.** The quality seed applies the design rubric, which is about *design* quality — and all three documents were sound designs. The correctness seed checks document *integrity*: placeholders, contradictions, planning-blocking ambiguity, unstated assumptions, missing success criteria. Two of the three instances are invisible to it by construction — `seam` and `family` sit in internally consistent documents and are wrong only from outside, against the rest of the repo's language, and nothing in the protocol looks outside.

`angle`/`pass` is different, and the design should say so rather than round it off. It lives *in the artifact*, so on its face it is an internal contradiction — and "internal contradictions" and "planning-blocking ambiguity" are in that checklist today. The claim is not that the existing bullets are out of scope; it is that they are empirically insufficient. Both were already in the `design` correctness cell when gh-7's own design review ran (`git show 4e32e0e~1`, line 29), and that review — two `sonnet` seeds, three `opus` resolvers, ~484k tokens — still shipped `angle` and `pass` used interchangeably; a `/grill-with-docs` pass found it minutes later. The reason is structural rather than a fluke: a reviewer hunting contradictions compares what sentences *assert*, and here every sentence asserts something true. The contradiction is in what one word *denotes* across them, which is visible only to a reviewer told to hold a term fixed and check its senses. That is what the against-itself clause instructs, and it is why the clause is a pointed restatement rather than a duplicate.

## Where the change lands

| Mode(s) | Seed | Concretely |
|---|---|---|
| `design`, `plan` | **correctness** | The prose-integrity checklist (table row `design`, inherited by row `plan`), plus a new below-table pass |

The same slot and the same shape as gh-7's input-contract completeness pass. `plan` inherits it through the `plan` row's existing "The prose checklist above" reference, and — as with gh-7 — the pass's own heading names both modes so a plan-mode prompt built from either reading of that phrase includes it. The `plan` row is not edited.

Nothing lands in the design rubric, which is the design/plan quality seed's lens **and** every resolver's judgment criteria in all three modes, making it the widest-broadcast text in the file. That ruling is gh-7's, unchanged, and it applies here for the same reason: this is a *noticing* obligation for a seed, not a statement of what "best long-term design" means for a decider.

**Why the correctness seed and not the quality seed — decided, not defaulted.** In `design` and `plan` mode there is no quality-seed slot distinct from the rubric: that cell's entire content is that the rubric *is* the lens. The ruling above therefore rejects the quality seed as well, and the live alternatives are the correctness seed or nothing. The pass fits neither seed's stated remit — that is what *Why the existing seeds miss all three* establishes, and it is why the gap existed — so it lands in the correctness seed on cost, which is exactly the rule gh-7 stated when it put the input-contract pass there: *"anything else lands there on its own cost argument, or not at all."* This is that rule's second exercise, taken deliberately. The cost is named rather than absorbed: the correctness cell's inline checklist no longer describes everything that seed does. What bounds the drift is the cell's own grammar, which separates the checklist from its below-table pointers — a third pass lengthens the pointer list, it does not loosen the checklist — and a pass that cannot make its own cost argument is a signal to restructure the section, not to add another pointer.

## The decision

**Trigger.** Only words the artifact introduces or adopts as the **name of a concept** — one it defines, coins, or borrows from another source. Deciding that is a semantic read, not a typographic one, and this repo's own docs show why: its design docs carry 49–146 bolded spans each, almost all ordinary emphasis (`**both**`, `**not**`, `**First:**`), and not one of this document's headings names a coined term. What keeps the trigger tight is not markup but that prose names concepts *sparsely and out loud* — a doc that coins a term almost always says so in the sentence that coins it ("we call this X", "borrowed from `codebase-design`"), so the artifact supplies its own evidence and the candidate set stays a handful regardless of word count. Typography is where a reviewer looks first, never the test it applies. Sparseness is the property that does not survive into `diff` mode (see Out of scope).

**Stopping conditions**, both stated in the trigger sentence itself so a reviewer reads them before doing any work:

1. **Never the repo's vocabulary at large.** This is not a glossary audit. An artifact introducing three named concepts checks three words, regardless of how large the repo's vocabulary is.
2. **Never a word the artifact uses in the sense the repo already has.** Without this, every use of `seed`, `resolver`, `tier`, or `mode` in a dev-flow design fires the pass.

Worst case is linear in the count of concepts the artifact names — a handful for any design doc that is not itself a glossary. This document names three (see *Applying the pass to itself*), against 71 bolded spans and 24 headings.

**The check, two clauses.**

- **Against the repo.** Glossary first (`CONTEXT.md` at the root, or the per-context files a root `CONTEXT-MAP.md` names), then grep the review's working directory for any term the glossary does not settle — restricted to shipped prose, skipping the artifact itself and `docs/superpowers/`.
- **Against itself.** One word carrying two senses, or two words carrying one — the `angle`/`pass` case, which no glossary can catch because both senses are new.

**Reportability rule.** Report only what you can quote: the artifact's sense, the colliding sense, and where the colliding one lives. "Define your terms" and "the vocabulary could be tighter" are not findings. As in gh-7, the trigger narrows *which artifacts get asked* and the reportability rule narrows *what may be said*. The two filter different things, and both are load-bearing: stopping condition 2 discards a word the artifact uses in the sense the repo already has — which ordinary English always is, so it is what stops an over-extracted `**both**` — while the reportability rule discards anything that cannot quote two distinct senses plus a location, forcing every finding into a checkable claim a resolver can reject in a single read.

**Findings only, and the fix is the resolvers' call.** A collision does not imply a rename. `seam` resolved the other way: the word stayed and `CONTEXT.md` gained an entry stating that this repo uses it at two levels. Both outcomes are legitimate, so the seed reports the collision and both senses and stops there.

**The fix lands in the artifact.** If a term needs a glossary entry, the artifact says so and the entry ships in the same commit as the behaviour it defines — gh-7's §6 precedent. The seed never writes `CONTEXT.md`; neither does the fixer, except as part of a change the artifact itself specifies. That boundary is what keeps this inside `adversarial-review`'s "owns the artifact end-to-end" contract.

## Why glossary-first-then-grep, and not either alone

**Glossary-only fails on the actual evidence.** `CONTEXT.md` did not exist when `seam` collided. And gh-7's own self-caught collision — its new `Trigger` glossary entry against the `Triggers on …` phrasing in every plugin's frontmatter — is a collision *with shipped prose the glossary does not cover*, which is a permanent property, not a transitional one. A glossary records the senses someone has already noticed. The senses that cause collisions are by definition the ones nobody noticed.

**Grep-only loses precision.** The glossary supplies the canonical sense and the explicit `Avoid:` synonym list, which is what lets a finding say "the glossary defines X as A, the artifact means B" instead of "this word appears elsewhere." It also settles most terms in one read, so the grep runs on the remainder rather than on everything.

**So: glossary first, grep the remainder.** Exhaustive on sources, narrow on surface. The cost is one file read plus a grep per unsettled term.

**The grep is scoped to shipped prose.** It skips the artifact itself — a grep of the working directory hits the artifact's own uses of every term it names, guaranteed, and those are the against-itself clause's job — and it skips `docs/superpowers/`, whose design and plan documents are immutable history rather than text the repo ships. That exclusion is not a nicety here: at the design stage, `docs/superpowers/specs/` holds every prior design this repo produced, and those are the densest prose in the repo about exactly these words — gh-7's spec alone argues at length about `seam`, `angle`, `pass`, and `trigger`, and carries a *"Rejected alternatives"* section stating senses that were considered and discarded. A seed grepping them would report senses the repo deliberately does not use. The repo has already ruled this way twice: gh-7's Out of scope calls those documents immutable records and excludes them from its verification greps, and this design excludes them from its own Blast radius grep. Without the clause the pass would be the only place that greps the repo without the exclusion its own author applies everywhere else.

**Graceful fallback, generalized.** Missing, empty, present-but-not-a-glossary, and named-by-a-`CONTEXT-MAP`-path-that-does-not-exist all produce one outcome — the glossary settles nothing about this term — and all have one correct response: fall through to the grep and say nothing about the glossary. The pass states it that way rather than naming only the absent case, because "present but settles nothing about this term" is the *modal* path, not an edge case: this repo's own `CONTEXT.md` settles ~20 terms, and most artifacts will name a concept it does not cover. The "grep and proceed silently" wording is lifted from `docs/agents/domain.md`, which is byte-identical to `setup-matt-pocock-skills/domain.md` upstream; what is added is that the silence is scoped to *the glossary's own state*, so it can never be read as suppressing a real collision the grep finds. The asymmetry worth naming: `domain-modeling`'s fallback for a missing glossary is *create it lazily*, and that path is closed to a findings-only seed.

**Deliberately not guarded**, having been considered: an enormous glossary (no repo in evidence has one, and the threshold would be a made-up number); a `CONTEXT-MAP.md` naming many contexts, where `domain.md`'s "relevant to the topic" scoping is dropped and cross-context term reuse is legitimate rather than a collision (zero multi-context repos in evidence, and adding a relevance judgment to a `sonnet` seed trades one imprecision for another); and a symlinked or binary `CONTEXT.md`. All four degrade into "settles nothing", which routes correctly.

## The `domain-modeling` question, settled

gh-7 rejected wiring in `domain-modeling` on mechanism: its body is user dialogue ("force the user to be precise", "offer to create an ADR"), and it *writes* repo state — neither of which a findings-only review leaf can do. **That rejection stands and is not reopened.** What this design takes is not the skill but the read habit, which the skill itself declares separable in its opening paragraph:

> Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.

`/grill-with-docs`, which found what five reviewers missed, is one line: "Run a `/grilling` session, using the `/domain-modeling` skill." Its glossary behaviour is entirely `domain-modeling`'s, and the part that did the work here is the part its own author says any skill can inline. gh-7 also removed a third, false disqualifier — that `domain-modeling`'s subject is project-wide vocabulary rather than the artifact under review — and this design is what replaces it.

## Working directory — one clause edited, so the dependency holds in shipped text

This is the **first seed pass that reads outside the artifact**. gh-7's input-contract pass is explicitly bounded to the artifact's own text ("no codebase spelunking for unnamed callers"); this one reads the glossary and greps the repo, so it depends on the correctness seed actually receiving the absolute repo root.

The Working directory section threads that root into "every spawned agent's prompt — seeds, resolvers, and fixers". But the sentence after it — *"Read-only reviewers receive absolute artifact/diff paths and need no entry"* — reads as a per-role split in which read-only reviewers get the artifact path *instead of* the root. Under that reading a prompt-builder ships a seed prompt with no repo root in it, this pass's "against the repo" clause is silently unusable on day one, and nothing in the file reveals it. Resolving that ambiguity here, in a document that never ships, does not reach the prompt-builder.

It is also not this pass's problem alone. Both `diff`-mode seeds are read-only reviewers that must reach the repository at two revisions — the quality seed "run against `BASE..HEAD`", the correctness seed filled with `[BASE_SHA]`/`[HEAD_SHA]` — so the under-specification already has two instances on `main` before this pass adds a third. The seed family, not this pass, is therefore the right place to fix it: a restatement inside the pass would be the per-instance fix every future repo-reading pass has to remember to repeat.

So line 20's third sentence is replaced (see the change list). "Need no entry" keeps its meaning — no cd, no worktree entry — and the sentence now also says the root reaches read-only reviewers rather than being withheld from them. The pass itself is not changed to compensate; its existing phrase "the review's working directory" names the value the section now guarantees.

## Applying the pass to itself

The check this change adds, run against this document. Candidate terms, and what the trigger does with each — `sense` is in the list precisely because it is bolded and still fails the trigger, which is the semantic step no markup rule performs:

- `collision` — already used in this repo in exactly this meaning (gh-7's design, "A collision this change must not repeat"). Same sense; no finding.
- `domain glossary` — `docs/agents/domain.md` and gh-7's design both call `CONTEXT.md` "the glossary". Same referent; no finding.
- `sense` — ordinary English, not a name for a concept. Trigger does not fire.
- Against itself: `pass`, `trigger`, `reportability rule`, `seed`, `resolver` are all used in the senses `CONTEXT.md` already defines. No finding.

Nothing to report, which is the expected result for a document written after the glossary existed.

## Rejected alternatives

**A rubric bullet ("use the repo's established vocabulary").** Rejected. Widest possible context cost — the rubric ships into every resolver in all three modes — to serve two modes' correctness seed, and it mislocates the work: the rubric tells a *decider* what good design means, and this is an enumeration for a *noticer*. Identical to gh-7's reasoning for both its families.

**Invoke or recommend `domain-modeling` / `codebase-design`.** Rejected — see above. The mechanism disqualifiers are unchanged; only the read habit is borrowed, inline.

**Gate the review on a glossary existing.** Rejected. It makes a shipped, general-purpose skill assume one person's documentation convention, turns a missing file into a halt (the pipeline's most expensive outcome), and would have been useless on the motivating instance, where no glossary existed.

**Have the seed write the missing glossary entry.** Rejected on two counts. Seeds are findings-only by construction — the property is in the prompts themselves so no caller has to enforce it — and writing `CONTEXT.md` is outside the artifact, which is the exact boundary that disqualifies `domain-modeling`. When an entry is warranted, the artifact specifies it and it ships with the behaviour.

**A third seed pass, or a separate "vocabulary" seed.** Rejected. It raises design/plan seed cost by 50% for one question and breaks the uniform two-seed shape the whole section and the provenance line are written around. The question fits in the existing correctness seed.

**Sharpen the existing "internal contradictions" bullet instead of adding the against-itself clause.** Rejected — though it is the closest alternative to the shipped design and the one a reader reaches for first. The checklist bullet is the shared boundary for within-document inconsistency, so putting the fix there is the right instinct; it fails on gating. The bullet has no trigger and no reportability rule, and it cannot acquire them without becoming this pass. Widened to name vocabulary, it asks every artifact whether any word carries two senses, over every word rather than over named concepts, with no bar on what may be reported — precisely the shape `CONTEXT.md`'s **Trigger** entry warns manufactures false positives. Kept in the pass, the clause inherits both gates for free and the two halves of one question stay in one place. The evidence that the bullet as it stands is insufficient is in *Why the existing seeds miss all three*.

**Cover `diff` mode in the same pass.** Rejected — see Out of scope.

## Out of scope

**`diff` mode — filed as #20.** Neither diff seed checks terminology today: the correctness seed is the pinned superpowers `code-reviewer.md`, whose "What to Check" list has no naming or vocabulary item anywhere in it, and the five quality angles are all structural. That is a real hole, and it leaves two gaps this change does not close — standalone `adversarial-review(<PR#>, diff)` on a PR that never had a design stage, and names invented during execution that no design could have contained.

It is deferred rather than bundled because **the trigger does not transfer**. In prose the candidate set is sparse and self-announcing: most words name nothing, and a doc that coins a term usually says so in the sentence that coins it. A code diff inverts both properties — every new function, field, local, and test helper *is* a name, and none of them announces whether it is a domain concept — so the discriminator becomes "names a domain concept, not an incidental identifier", a judgment a `sonnet` seed makes unreliably across dozens of identifiers per diff. The economics punish that: `config`, `client`, `handler`, `result` always grep-hit somewhere, and one false-positive resolver group measured ~86k tokens in gh-7's run, hundreds of times the entire prose addition. Bolting a second, weaker trigger into this paragraph would degrade the one that works.

#20 records the sketch that does work — invert the direction, iterating over the glossary's fixed entry count rather than the diff's unbounded identifier count — and the open question it must answer, that such a check has no fallback in a repo with no glossary.

**`docs/adr/`.** `docs/agents/domain.md` has agents read ADRs as well as the glossary, but ADRs record decisions, not vocabulary. The pass reads the glossary only.

**`CONTEXT.md`.** No entry is added. gh-7 added none for its input-contract pass either; `Pass`, `Trigger`, and `Reportability rule` already define the shape this pass is an instance of, and `Pass` — unlike `Angle` — does not enumerate its instances. Adding one would be the glossary growing an entry per check.

## Context cost

`adversarial-review/SKILL.md` is 2,237 words today. The addition is 217 words in the pass, plus a net 15 in the Working directory section and a net 2 in the `design` cell — 234 words, about **10.5%** of the file, ~330 tokens.

Measured against gh-7's real review invocation of 484,005 tokens, that is roughly **0.07%** — the orchestrator's whole-file load plus one seed prompt. The number on the other side of the trigger is the one that matters: a single false-positive resolver group measured 86,022 tokens, ~260× this entire addition. Every word spent on the trigger, the grep scoping, and the reportability rule is therefore lopsidedly worth it, which is why all three are stated in full rather than compressed.

Structural dilution is worth separating from the word count. The trigger sentence — the one an artifact naming no new concept reads before stopping — is unchanged by everything the review added; the grep scoping and the generalized fallback sit in the check body and the fallback, read only after the trigger has already fired. The two costs the token count misses, per gh-7: **instruction dilution**, mitigated by that lead-with-the-trigger structure, and **a standing obligation**, one more pass every future protocol change must keep coherent, which is why the pass names no tier.

## Exact change list

Four files. Every wording below is literal.

### 1 & 2. `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`

A declared `check-sync.py` mirror pair. **Every edit below lands byte-identically in both files.** None of the new or edited text contains a `dev-flow` or `dev-flow-worktree` token, so the two copies compare equal in every touched region before canonicalization does anything.

Three edits: two in-place line replacements and one two-line insertion. Both replacements are above the insertion point and in place, so neither shifts it. Line numbers are the current (pre-change) file, which is 85 lines.

#### Line 20 — Working directory, the read-only-reviewer sentence

Only the third sentence changes; the halt rule, the threading sentence, the fixer sentence, the `EnterWorktree` rules, and the override sentence are byte-identical. Replace the whole line with:

```
**Working directory (resolve once, thread always).** Resolve the working directory exactly once at invocation: the explicit `working-dir` argument if given, else the invoking checkout root (`git rev-parse --show-toplevel`), normalized to an absolute path; resolution failure (not a git repo) is a loud halt at invocation, because the contract requires committing. Thread that absolute path into every spawned agent's prompt — seeds, resolvers, and fixers — so no spawned agent derives its location from inherited cwd (process cwd is global mutable state; parallel fixers make ambient cwd a race). Read-only reviewers receive that root as well as absolute artifact/diff paths — they read, grep, and `git -C` it in place, and need no entry. Write-side fixers address the root explicitly with `git -C <path>` and absolute file paths (harness worktree-entry via `EnterWorktree` is not accepted from these cwd-pinned subagents, and explicit addressing is in any case the only mechanism that works for standalone reviews of checkouts outside `.claude/worktrees/`, which `EnterWorktree` rejects). The `working-dir` argument is an override only — omission cannot produce ambient-cwd behavior.
```

#### Line 29 — Seed passes table, the `design` row

The correctness cell points at the one below-table pass it has; a second is added, so the cell must name both or the new one is unreachable by a prompt-builder that resolves the cell. Replace the whole line with:

```
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria — plus the input-contract completeness and terminology-collision passes (below). |
```

Only the correctness cell changes; the quality cell is verbatim as today. **Line 30 (the `plan` row) is not edited** — its "The prose checklist above" reference carries the addition, and the new pass names both modes in its own heading.

#### Insert after line 44 (the input-contract completeness pass) — the terminology-collision pass

Insert exactly two lines: one empty line, then this line. Placing it after the input-contract pass keeps the two design/plan notes contiguous and last in the section, matching the layout gh-7 established.

```

**Terminology collision — the design *and* plan correctness seed:** applies only to words the artifact introduces or adopts as the name of a concept — one it defines, coins, or borrows from another source — never to the repo's vocabulary at large, and never to a word the artifact uses in the sense the repo already has. For each, check twice. **Against the repo:** read the domain glossary first (`CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names), then grep the review's working directory for any term the glossary does not settle — a sense that lives only in shipped prose is still a collision. Grep shipped prose only: skip the artifact itself, and skip `docs/superpowers/`, whose design and plan records are history rather than shipped text. **Against itself:** one word carrying two senses, or two words carrying one. Report only what you can quote: the artifact's sense, the colliding sense, and where the colliding one lives; "define your terms" is not a finding. Whether the fix is a rename or an explicit statement that the word spans two levels is the resolvers' call. If the glossary is missing, empty, or settles nothing, grep and proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one.
```

#### Resulting file shape

Both copies go from **85 to 87 lines**.

| Line | Content |
|---|---|
| 20 | Working directory (edited, in place) |
| 29 | `design` row (edited, in place) |
| 30 | `plan` row (unchanged) |
| 44 | input-contract completeness pass (unchanged) |
| 45 | empty (new) |
| 46 | terminology-collision pass (new) |
| 48 | `## The design rubric` (unchanged, was 46) |

Everything from the old line 45 onward shifts by +2. The declared exception's line (12) is above every edit and does not move.

**Explicitly unchanged in these files:** the `diff` and `plan` table rows, the four `/simplify` angle bullets and the seam-placement angle, line 32, the angles-block header, the input-contract completeness pass, the design rubric (all nine bullets), the Resolution procedure, the Model section, the provenance line, Review integrity, the Contract, and the frontmatter `description`. Within the Working directory paragraph, only the read-only-reviewer sentence changes.

### 3 & 4. Version bumps

- `plugins/dev-flow/.claude-plugin/plugin.json` — `"version": "2.4.0"` → `"version": "2.5.0"`.
- `plugins/dev-flow-worktree/.claude-plugin/plugin.json` — `"version": "1.6.0"` → `"version": "1.7.0"`.

Mandatory, not cosmetic: the install cache is version-keyed, so an edit at an unchanged version is never picked up on re-sync. Minor rather than major — the skill's invocation signature, contract, provenance format, and mode set are unchanged; only seed content and one clause of the working-directory rule change.

## Sync constraint — how `check-sync.py` still passes

**Check B (mirror pair `adversarial-review`)** requires the two files to be line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, except the declared exception at line 12.

1. **All three edits land in both files.** A one-sided edit produces an undeclared-divergence failure naming the line.
2. **The insertion is symmetric, so line counts stay equal.** Both files go 85 → 87. An asymmetric insertion is a `LINE_COUNT_FIX` failure and could not be declared as an exception even deliberately.
3. **No new variant token is introduced.** The added and edited text contains no `dev-flow` / `dev-flow-worktree` occurrence.
4. **The declared exception still fires and does not go stale.** It covers line 12, above every edit, which does not shift.

**Check A (manifest descriptions)** compares `name`, `source`, and `description` between each `plugin.json` and its marketplace entry, and does not read `version`. This change edits only `version`, so `.claude-plugin/marketplace.json` is not touched.

**The hand-mirrored pipeline `SKILL.md` pair is not edited at all**, so no hand-mirroring risk is incurred.

## Blast radius

A repo-wide search of tracked files outside `docs/superpowers/` for `input-contract`, `correctness seed`, and `prose-integrity` returns hits **only** in the two `adversarial-review/SKILL.md` copies. Specifically confirmed to need no edit:

- **Both pipeline `SKILL.md` copies** — they invoke the review by mode and delegate seed content entirely; neither enumerates or describes a seed pass, and neither restates the working-directory rule (dev-flow uses no worktree and says so).
- **Both `README.md` files** — no seed/pass/checklist content.
- **`.claude-plugin/marketplace.json`** — no `description` changes; Check A does not read `version`.
- **`CONTEXT.md`** — no entry added (see Out of scope).
- **`CLAUDE.md`** — the mirrored-pair verification rule gh-7 landed already covers this change as written; no new rule and no rescoping is needed, so it is not edited.
- **`scripts/check-sync.py`**, `.github/workflows/`, `docs/agents/*.md` — untouched.

## Verification

1. `python3 scripts/check-sync.py` — passes.
2. `claude plugin validate .` — passes; the 8 missing-author warnings are expected.
3. **Residue grep (always, per `CLAUDE.md`).** All three of these return **no hits** under `plugins/`, each naming text this change removes or supersedes:

   ```sh
   git grep -n -e 'input-contract completeness pass (below)' \
              -e 'Read-only reviewers receive absolute artifact/diff paths' \
              -e 'never flag its absence or propose creating one' -- plugins/
   ```

   The first two are the exact phrases the two in-place replacements delete; a hit means one side of the mirror pair was missed. The third never existed in `SKILL.md` — it is the pre-review draft of the pass's final sentence, and a hit means the stale block was applied instead of the one in §Exact change list.
4. **Design conformance — all three blocks landed verbatim, in the right place.** This is the one step steps 1–3 structurally cannot provide. Step 3's residue grep is tied to the two in-place replacements and says nothing about the insertion, and `check-sync.py` compares the two copies only to *each other*, so a word mangled identically in both passes it at the correct 87 lines. This check reads the expected text from this design file on disk — never retyped — and requires a byte-for-byte line match in each copy, plus, for the insertion, that it sits directly after its anchor line. The anchor matters on its own: the pass inserted after the `Pinned template` paragraph instead would leave a diff-mode note trailing the two design/plan notes and pass every other check here. It also asserts each copy is 87 lines, using `check-sync.py`'s own `wc -l` convention so "87" means the same thing in both steps. Full-line equality in both copies is strictly stronger than gh-7's separate presence grep for each insertion's opening phrase, so no such step is listed here. Copy the script exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing. **The fence is unindented on purpose** — a `python3` heredoc indented under the list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-28-gh-16-terminology-collision-design.md"
FENCE = chr(96) * 3
blocks, cur, mode = [], None, None
for line in Path(DESIGN).read_text(encoding="utf-8").split("\n"):
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
assert [len(b) for b in blocks] == [1, 1, 2], "design code-block shape changed; stop and re-read the design"
SPEC = [("line 20, working directory", blocks[0], None),
        ("line 29, design row",        blocks[1], None),
        ("terminology-collision pass", blocks[2], "**Input-contract completeness")]
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
bad = []
for path in PAIR:
    L = Path(path).read_text(encoding="utf-8").split("\n")
    if L and L[-1] == "":
        L.pop()
    if len(L) != 87:
        bad.append(("file length", path, "%d lines, want 87" % len(L)))
    for name, want, anchor in SPEC:
        at = [i for i in range(len(L) - len(want) + 1) if L[i:i + len(want)] == want]
        if len(at) != 1:
            bad.append((name, path, "found %d times, want exactly 1" % len(at)))
        elif anchor is not None and not L[at[0] - 1].startswith(anchor):
            bad.append((name, path, "sits after %r, want %r" % (L[at[0] - 1][:40], anchor)))
for name, path, why in bad:
    print("MISMATCH:", name, "in", path, "--", why)
print("design-conformance:", "FAIL" if bad else "OK")
sys.exit(1 if bad else 0)
PY
echo "exit=$?"
```

   Expect exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — re-paste that block from §Exact change list and re-run from step 1. The shape assertion (`[1, 1, 2]`) fires if this document's plain-fenced blocks are ever added to, removed, or reflowed: that is deliberate, because the blocks are indexed positionally. The script's own fence carries the `sh` info string and is therefore skipped by the `mode == ""` filter, so adding or editing a verification step never disturbs that index — keep it that way.

5. Both `plugin.json` versions read `2.5.0` and `1.7.0`.
6. **Behavioural check, on this design doc itself.** The pass is meant to fire on documents like this one. Its design-stage review is the first live exercise: a run that reports a collision here should be able to quote both senses and a location, and a run that reports "consider defining your terms" is evidence the reportability rule is too weak to have shipped.

## Assumptions recorded

- **`CONTEXT.md` is the glossary filename in repos that have one.** Taken from `docs/agents/domain.md`, which is byte-identical to the upstream file `setup-matt-pocock-skills` installs. Repos that use a different filename get grep-only behaviour, which is the fallback path and is correct rather than broken.
- **A `sonnet` seed can pick a design doc's named concepts out of its prose.** This is the trigger's load-bearing assumption, and because it is a semantic judgment it can fail in either direction — not only the convenient one. Under-extraction is the status quo: collisions missed, nothing spent. Over-extraction — an emphatic `**both**` read as a coined term — costs seed-side reads and greps, and two independent filters stand between it and a resolver group: the second stopping condition discards every word the artifact uses in the sense the repo already has, which is what ordinary English always is; the reportability rule then discards anything that cannot quote two distinct senses and the place the other one lives. So the failure this assumption can produce is seed cost, not the 86k-token one, and the design does not depend on extraction erring conservatively.
- **Line numbers 20, 29 and 44 are current as of `4e32e0e`.** The plan re-derives them by content match rather than trusting the numbers.
