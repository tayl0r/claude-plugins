---
dev-flow:
  slug: gh-20-diff-terminology
  stops: [post-design]
  docs: commit
---

# gh-20 + gh-22: terminology coverage for diffs, and drift coverage for designs and plans

## Goal

Close **#20** and **#22** with one change to `adversarial-review`'s seed passes, in two complementary halves plus the one repair the second half exposes:

- **#20 — `diff` mode.** A trigger-gated **sixth quality angle**, *glossary conformance*, so a diff that uses a glossary term for something the glossary does not define — or reintroduces a synonym the glossary marks as one to avoid — is reported as a finding instead of shipping. The angle iterates the **glossary's** entries and searches the diff for each, never the reverse.
- **#22 — `design` and `plan` mode.** A **drift clause on #16's existing terminology pass**, not a new pass, so an artifact that reaches for a name the glossary explicitly rejects is reported at the stage where it is actionable and where the artifact is prose. The pass is renamed **terminology collision and drift** to match what it now covers.
- **The repair the drift clause exposes.** Enforcing `CONTEXT.md`'s `_Avoid_: boundary` against this repo finds exactly one real defect in shipped text: the design rubric names the **Seam** concept "boundary" on two of its bullets, one line away from a third bullet that calls the same thing a seam. Those two words are fixed here rather than tolerated. See *Does `CONTEXT.md`'s `_Avoid_: boundary` entry survive a check that enforces it?*, which is the section the whole glossary question is settled in.

Both halves are findings-only and read-only: neither renames anything, neither writes `CONTEXT.md`, neither proposes creating one. Nothing lands in the verbatim `/simplify` four-bullet block, the resolver tier, or the `diff` correctness seed. Nothing *new* lands in the design rubric — the only rubric edit is the two-word terminology repair, which adds no obligation and no length.

**Which check covers which artifact, and why the two do not overlap.** The angle reads a **diff's added lines of shipped text**, skipping design and plan records under `docs/superpowers/`. The pass reads **the artifact under review** — a design doc or a plan doc, which is exactly what the angle skips. That skip is not an oversight the pass patches over; it is the reason this half belongs on the pass. A `diff`-mode seed asked to judge a design record would have to separate *mention* from *use* across prose whose subject **is** the vocabulary — 985 of 996 added lines on `0a8a158` — while a `design`-mode seed reading that same document *as the artifact* is doing the ordinary thing: judging the prose it was handed. Together they cover shipped text at merge time and prose at authoring time, with nothing asked twice.

One clarification the two halves make necessary, because both mention the same path: the pass's `docs/superpowers/` exclusion governs its **repo-side grep**, never its read of the artifact. A design doc under review is read in full regardless of where it lives; only the corroborating grep skips that directory.

## Scope check — one change, one mirrored pair

This is not two subsystems. It is one file's seed passes: one angle added to one block, one clause added to one pass in the same file, and two words repaired in the rubric that the clause proves wrong — all inside one `check-sync.py`-declared mirror pair, plus the glossary entry that enumerates the angles block's contents and the two version bumps the install cache requires. **Five files, one commit, no decomposition** — the same five as the #20-only design, because everything #22 adds lands in files that change anyway.

Splitting #22 into its own PR was considered and rejected. The two halves share the glossary read, the naming discriminator, the reportability shape, and the never-flag clause — three of which this design ships as byte-identical spans across both. Landing them separately means writing those spans twice, reviewing the same trade twice, and bumping two plugins twice, while leaving the first PR's *Honest limit* section asserting a shipped-text defect the second PR fixes.

## The gap, restated precisely

Confirmed by reading both `diff`-mode seeds and the `design`/`plan` correctness seed on `main` (`0a8a158`):

- The `diff` **correctness** seed is the pinned superpowers `code-reviewer.md`, used as designed. Its "What to Check" list covers plan alignment, code quality, architecture, testing and production readiness, with no naming, vocabulary or terminology item. The template is pinned and filled at four placeholders only, so `diff`-mode correctness cannot be extended without unpinning it.
- The `diff` **quality** seed's five angles — reuse, simplification, efficiency, altitude, seam placement — are all structural. None asks what anything is called.

So any `diff` coverage has to be a sixth quality angle. That is #20's constraint and it survives inspection.

**What #16's pass leaves open on the diff side.** #16 (shipped in `0a8a158`) added a terminology-collision pass to the `design`/`plan` **correctness** seed. It catches terms where they are coined, which is where all of its evidence sat. Two holes survive:

1. **Standalone `diff` reviews get nothing.** `adversarial-review(<PR#>, diff)` is a supported entry point in the Invocation contract, and a PR that never went through dev-flow has no design stage to have caught anything.
2. **Names invented at execution time are never checked.** A design says "a terminology pass"; the implementer writes `checkVocab()`. No design-stage reviewer can see that name.

**Honest narrowing of the diff half.** The angle designed here closes hole 1 completely — every `diff` review of a repo with a glossary now runs a terminology check — and closes hole 2 **only where the invented name collides with a glossary term**. An execution-time name colliding with a sense that lives only in shipped prose, which is what #16's grep half catches for design docs, is still uncovered in `diff` mode. That narrowing is deliberate and is the entire reason the check is affordable; see *The decision*. #20's framing implies hole 2 is closed outright, and it is not.

**What #16's pass leaves open on its own side.** #16's trigger is *"words the artifact introduces or adopts as the name of a concept — one it defines, coins, or borrows from another source — never to the repo's vocabulary at large, and never to a word the artifact uses in the sense the repo already has."* Both of its exclusions fire on drift, so the trigger never gets off the ground:

- An artifact reaching for *"the shared boundary"* is not **introducing** the word as the name of anything. It is reusing a phrase the repo already uses, in passing.
- It is arguably using the word *"in the sense the repo already has"* — because the repo's own design rubric uses it in that sense. That exclusion, which exists to stop the pass auditing ordinary vocabulary, is exactly what shields the drift.

#22's evidence is #16's own review: an earlier draft's `family` collision was reworded to *"the shared boundary"* — walking straight into **Seam**'s `_Avoid_: boundary` — in a document written by the author of the collision check, and the shipped check would not have flagged it. This is hole 3, and it is the one #22 closes.

## Where the change lands

| Mode | Seed | Concretely |
|---|---|---|
| `diff` | **quality** | A sixth angle in the angles block, outside the verbatim `/simplify` four-bullet list, with the block header and the `diff` row's quality cell updated to name it |
| `design` and `plan` | **correctness** | A drift clause on #16's existing terminology pass — a clause, not a new pass — with the pass renamed to match what it now covers and the `design` row's correctness cell updated to name it |
| all three | **the design rubric** | Two words, `boundary` → `seam`, on the two bullets that name the **Seam** concept by the name `CONTEXT.md` rejects. No obligation added, no length added |

The angle sits in the same slot and takes the same shape as gh-7's seam-placement angle, which is the precedent #20 cites. No *check* lands in the design rubric — that ruling is gh-7's and gh-16's, unchanged, and applies here for the same reason: the rubric is the design/plan quality seed's lens **and** every resolver's judgment criteria in all three modes, making it the widest-broadcast text in the file, and a noticing obligation for one seed in one mode is not a statement of what "best long-term design" means for a decider. The two-word repair is not a check; it is the rubric saying what it already means in the vocabulary the glossary settles, and it is argued in its own section below.

Nothing lands in the four `/simplify` bullets, which are transcribed verbatim from a harness built-in with no readable file to point a subagent at. Editing them would silently fork a quotation.

## The decision — iterate the glossary, not the diff

The angle's three stages, in order:

1. **Read the glossary.** `CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names. No entries to iterate → the angle stops here and reports nothing.
2. **Grep, mechanically.** For each entry's term, and for each synonym the entry marks as one to avoid, grep the diff's **added lines of shipped text** for that term — case-insensitively, and in the joined spellings a multi-word term takes as an identifier — skipping design/plan records (`docs/superpowers/`). Those discuss the vocabulary rather than ship it, so every glossary term appears in them by construction — in *mention* rather than *use*, a distinction harder to draw than the naming discriminator this angle is built on. #16's pass excludes the same path for the same reason ("history, not shipped text"). Literal, cheap, and on shipped text most terms return zero hits in most diffs.
3. **Judge, only on hits.** A hit is a candidate only where the diff uses the term as a *name*, and then only if it names something the entry does not define, or reintroduces an avoided synonym for the concept it does.

### What the fixed-N argument buys, and what it does not

#20 says the glossary's entry count being "small, fixed, and independent of diff size … is what kills the false-positive problem." That is half right, and the half it misses is where the design work is.

Fixed N bounds **how many questions get asked**: 17 terms plus 6 avoided synonyms in this repo, 23 literal searches, the same number on a 40-line diff and a 4,000-line one. That is a real and decisive win over the diff-side direction, whose candidate set grows with the diff.

Fixed N does **not** bound **how many wrong answers come back**. Glossary terms are frequently ordinary English — this repo's glossary alone contains `pass`, `family`, `stop`, `artifact`, `angle`, `trigger`, `seam`, and the avoided synonym `boundary`. A Python diff has `pass` on every other function stub; a CI diff has `artifact` throughout; `boundary` appears 32 times in this repo's own shipped text, almost all of it meaning "stage transition". Step 2 will hit constantly, and on this repo's own diffs almost every hit is in prose *about* the vocabulary rather than prose that ships it. Measured on `0a8a158`, the last comparable change: **985 of its 996 added lines were dev-flow's own design and plan records**, carrying **285 of the 296 glossary-term hits** (`pass` 103, `seed` 60, `artifact` 48) and **all five** of its avoided-synonym hits. Its 11 added lines of shipped text carried 11 term hits and no avoided synonym at all. Two things then have to stop the remainder from reaching a resolver group, because gh-7's run measured one false-positive resolver group at **86,022 tokens**. The first is step 2's scope: shipped text only. The second is step 3.

### The naming discriminator

That something is step 3: **a hit counts only where the diff uses the term as a name** — an identifier, a field, a type, a user-facing or logged string, or prose that labels a concept. A term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate.

This is a narrower judgment than the one #20 correctly rejects for the diff-side direction. There, the seed must decide *"is `checkVocab` a domain concept?"* across dozens of unfamiliar identifiers with no reference to compare against. Here the term is fixed and supplied, the reference sense was read verbatim from the glossary one step earlier, and the question is only *"is this occurrence a name, and does it mean that?"* — a comparison, not an invention. Two live examples from this repo, both of which the discriminator handles correctly:

- The design rubric's *"Judge findings together, not in isolation"*. `judge` is an avoided synonym for **Resolver**. Here it is a verb describing an act, naming nothing. **Not a candidate.**
- The pipeline files' *"at each artifact boundary"*. `boundary` is an avoided synonym for **Seam**. Here it means a stage transition, which is not the concept **Seam** defines. **Not a candidate** under the second clause even if read as a naming use.

The same sentence carries the same load in the drift clause, which is why it is shipped **byte-identically** in both places; see *The #22 half*.

### The avoided-synonym half is a different failure, and needs saying so

#20 asks for `Avoid:` synonyms on the grounds that "a diff reintroducing an avoided synonym is the same failure." It is not quite the same failure, and collapsing them would leave the check unstatable.

- A **collision** is one word carrying two senses: the glossary's and the artifact's.
- **Drift** is one concept carrying two names: the glossary's preferred term and a name it explicitly rejected.

*Artifact* here is `CONTEXT.md`'s own term — "the single thing one review runs against — a design doc, a plan doc, or a branch diff" — so the distinction is stated once and used by both halves of this change. #22 asks for exactly that: it says the distinction "should be reused verbatim rather than re-derived," and the only word this generalization touches is the one that would otherwise pin the definition to `diff` mode.

They share a trigger surface, a search, and a reportability shape, which is why each half belongs in one place rather than two. But their candidacy clauses are inverses — a collision requires the artifact's sense to *differ* from the entry's, drift requires it to *match* — so the shipped text states both, in one sentence each, rather than one and a hand-wave. `docs/agents/domain.md` already carries the repo-side rule ("Don't drift to synonyms the glossary explicitly avoids"); this change makes it checkable at both of the stages that can see a name.

The half is nearly free on the angle side: the synonyms sit in the entry the seed just read, and the match is literal.

### The reportability rule

Report only what can be quoted: **the glossary's sense, the diff's sense, and the `file:line` where the diff's sense lives.** Same rule as #16, same reason — it is the second filter, after the naming discriminator, standing between a step-2 hit and an 86k-token resolver group. `"this name is confusing"` is not a finding, exactly as `"define your terms"` is not one in #16.

Findings only. A mismatch does not imply a rename, so it is reported either way; whether to rename is the resolvers' call. This mirrors #16's ruling, for #16's reason: a seed that finds one and privately judges the rename unwarranted is indistinguishable from the gap being closed.

## The #22 half — a drift clause on #16's pass

### The shape chosen

**One pass, two labelled halves, one glossary read.** The pass keeps every sentence #16 shipped. Three things change:

1. The glossary read is **hoisted** out of the `Against the repo:` clause to the pass's first sentence, because both halves need it. This is the only structural edit, and it removes a read rather than adding one — the drift half would otherwise have to restate the glossary-location clause a third time in the same file.
2. The existing trigger sentence is prefixed **`**Collision**`**, scoping it to the half it always described. Without that prefix the pass would open with "applies only to words the artifact introduces or adopts as the name of a concept" and then contradict itself two sentences later.
3. A **`**Drift**`** clause is added after `Against itself:`, with its own trigger (only the names an entry marks as ones to avoid), the byte-identical naming discriminator, a mention-versus-use exclusion the collision half must not inherit, and its own arm of the reportability rule.

The full replacement text is in *Exact change list*. The design-row cell of the Seed passes table changes with it, because it names the pass.

### Why the pass is renamed

The heading becomes **Terminology collision and drift**. This is not cosmetic. This document's own distinction says a collision is one word carrying two senses; a pass called *terminology collision* that also reports drift makes `collision` carry two senses — the narrow one the pass defines and a loose "terminology problem" one in its own heading — in the file that ships the check for exactly that failure. It is the same error this design refused when it declined to call the new angle "terminology collision", and refusing it there while committing it here would be incoherent.

The rename also corrects something that was already slightly wrong: `Against itself: one word carrying two senses, **or two words carrying one**` is *drift*, artifact-internal, and #16 shipped it under a heading that names only collision. So the pass has covered both failures since `0a8a158`; what #22 adds is the **glossary-side** arm of the drift half — comparing the artifact against the names the glossary rejects, rather than only against itself.

### The alternatives rejected

**A separate `Glossary drift` pass on the design/plan correctness seed.** The obvious shape, and the one #22 explicitly rules out ("a drift clause on #16's existing pass, not a new pass — it shares the pass's trigger surface, its glossary read, and its reportability rule"). Inspection agrees. A second pass would restate the glossary-location clause, the findings-only rule, and the never-flag clause a third time in one file — roughly 60 words of pure duplication for a check that shares all three — and would take the correctness seed from two passes to three, which is the cost #16 already refused when it declined a separate vocabulary seed. The one thing it buys is a heading a reader can jump to, and the labelled `**Drift**` clause buys that for one word. The economy argument is not the whole case, and on its own it would be the wrong axis — seed-side reliability, not prose length, is why this architecture exists. Nothing here measures whether a seed applies four judgments from one paragraph as reliably as two shorter passes, so the merge rests on a property that does not need measuring: the glossary read, the reportability rule, the findings-only rule and the never-flag clause are the screens that keep this check off the 86k-token path, and stating each once with an explicit *"for a collision … for drift"* branch makes it structurally impossible to ship one half without them. A split restates four false-positive screens in a second place inside one file, where `check-sync.py` proves nothing — it only ever compares the two mirror copies to each other — and where divergence is silent. The mis-parses the merged shape actually risks are the cheap ones: applying either half's trigger to the other under-detects, which is the status quo. **The threshold for revisiting, stated so a future reader has a rule:** split when a third top-level trigger joins Collision and Drift, or when a run reports drift without the entry's preferred term and a location — the observable signature of the shared reportability arm being missed.

**Fold drift into the existing `Against itself:` clause.** Tempting, because that clause already says "two words carrying one". Rejected: its entire property is that it compares the artifact to *itself* and needs no external read. Hanging a glossary comparison off it gives one clause two triggers with different inputs — the "one paragraph, two unrelated triggers" degradation #16 refused when it declined to bolt a diff trigger onto its own pass. The glossary-side arm is stated separately for the same reason `Against the repo:` is.

**Make the `diff` angle cover design docs too, and skip #22.** Rejected, and #22 rejects it first: the angle's scope clause exists because separating mention from use across ~1,000 lines of prose about the vocabulary is a harder judgment than the naming discriminator. Removing the scope clause to save a clause on the pass would trade the cheapest filter this design has for the most expensive judgment it avoids.

### Why the drift half stays bounded

The trigger is the smallest in the file: **only the names a glossary entry marks as ones to avoid**. In this repo that is 6 names from 3 of 17 entries. Fixed, tiny, independent of artifact size, and read from a file the collision half already opens. Three of the six — `finder`, `first-pass reviewer`, `arbiter` — occur exactly once each in tracked shipped text, and each of those single occurrences is the `_Avoid_:` line that names them; they will never fire. `group agent` does fire, hyphenated, twice per mirror copy, and is repaired by this change — see *Does `CONTEXT.md`'s `_Avoid_: boundary` entry survive a check that enforces it?*. The false-positive load lands entirely on the two that are ordinary English, `judge` and `boundary`, which is precisely what the naming discriminator and the concept clause are for, and precisely why the next section exists. The clause also asks for a judgment this design calls harder elsewhere — the *mention*-versus-*use* distinction the angle avoids by path-excluding `docs/superpowers/` outright. The asymmetry is conceded rather than hidden: the pass cannot path-exclude the artifact from itself, because the artifact is what it reads, and the genre of artifact that discusses vocabulary is a recurring one here (gh-16, gh-20, gh-22 and successors). What makes the same judgment affordable here and not there is scale. The angle would need it for all 23 searched terms across ~1,000 lines of prose whose subject *is* the vocabulary; the drift clause needs it for 6 fixed names, on one document, where the mention genres are three and enumerable — quoting the glossary, quoting or describing text under repair, reporting a prior record — which is why the clause names those three rather than asking for the distinction in the abstract. Without it the clause fires on every artifact that proposes to *fix* drift, since such an artifact must quote the text it repairs; the measurement is in *Applying the pass to this document*.

### What it costs per run, priced honestly

The angle is carried by one seed prompt in one mode. The pass is carried by one seed prompt in **two** modes, so a dev-flow run pays the drift clause at the design stage and again at the plan stage — and every future run pays it again. A false positive here **recurs** rather than costing once.

That asymmetry is the reason the `_Avoid_: boundary` question had to be settled before this clause could ship, and the reason the answer had to be a repair at the source rather than a tolerance. A recurring finding is not priced at one 86k-token resolver group; it is priced at one per run, forever, until someone changes the text that causes it.

## Does `CONTEXT.md`'s `_Avoid_: boundary` entry survive a check that enforces it?

The #20-only draft of this design ruled the glossary out of scope and asserted, without testing it, that the naming discriminator carried the entry. #22 makes the question live, because a design/plan-mode drift clause runs on every dev-flow artifact forever. It is tested here.

**What `_Avoid_:` is specified to mean.** `docs/agents/domain.md` states the rule it produces: *"When your output **names a domain concept** …, use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids."* The scope is conditioned on naming the concept. So `_Avoid_: boundary` under **Seam** forbids calling *the Seam concept* "boundary". It is not, and has never been, a ban on the word. Every `_Avoid_:` entry in the file is concept-scoped this way; **Seam**'s is not special.

**The counterexamples, counted rather than gestured at.** Tracked shipped text outside `docs/superpowers/` contains **32** occurrences of `boundary`/`boundaries`:

| File | Count |
|---|---|
| `plugins/dev-flow/skills/dev-flow/SKILL.md` | 9 |
| `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md` | 5 |
| `plugins/dev-flow/README.md` | 4 |
| `plugins/dev-flow-worktree/README.md` | 4 |
| `plugins/dev-flow/skills/adversarial-review/SKILL.md` | 2 |
| `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md` | 2 |
| `.claude-plugin/marketplace.json` | 2 |
| `CONTEXT.md` | 2 |
| `plugins/dev-flow/.claude-plugin/plugin.json` | 1 |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | 1 |

They split three ways, and the split is not close:

- **1 is the entry itself** — `CONTEXT.md:67`, the `_Avoid_:` line. The never-flag clause puts the glossary's own state outside every finding, in both halves, byte-identically.
- **27 name a stage transition** — "at each artifact boundary", "at every stage boundary", "the stop boundaries", "not a resume boundary", and `CONTEXT.md`'s own **Stop** entry, *"A boundary where the pipeline halts and hands control back."* That is a different concept from **Seam**: a point in the pipeline's timeline, not a place where behaviour can be altered without editing in that place. The drift clause's second condition — *"only where it names the very concept its entry defines"* — excludes all 27, and excludes them on the easiest grounds available. The question is not the semantic one ("is this a naming use?") but a comparison against a definition read one step earlier ("is this the **Seam** concept?"), and the answer is visibly no.
- **4 name the Seam concept** — the design rubric's *"put the fix at the shared boundary so current and future members inherit it"* and *"zooming out finds the right boundary, it doesn't add layers"*, two lines, mirrored into both copies.

**Those 4 are not false positives. They are correct findings, and the evidence is not opinion:**

1. **Seam** is *"a place where behaviour can be altered without editing in that place."* The shared place of a known family, where one fix lands so "current and future members inherit it", is that place by definition.
2. **The rubric already calls it a seam, one bullet later.** `SKILL.md:55` reads *"Prefer correct-by-default **seams** over designs where each caller must remember a flag, ordering, or manual step."* One concept, two names, in adjacent bullets of the same nine-bullet list — the textbook shape of drift, in shipped text, in the file this change edits.
3. **gh-7 read `:58` that way itself.** Its design declined to add a seam bullet to the rubric on the grounds that *"the rubric already carries 'zooming out finds the right boundary'"* — treating that line as the rubric's existing statement about seams — and then named the angle it shipped **seam placement**.

**So the entry survives, and the answer is neither (a) nor (b) as posed.** The discriminator carries 27 of the 28 live occurrences, on the clearest possible grounds. It does not carry the remaining 4, and it should not: they are a real defect the entry correctly identifies. **The right response to a correct finding is to fix what it found, not to weaken the rule that found it.** This change therefore replaces `boundary` with `seam` on `SKILL.md:54` and `:58` in both copies, and leaves `CONTEXT.md`'s **Seam** entry byte-identical. After the repair, every remaining `boundary` in shipped text names a stage transition.

**The same test, run over the other five rejected names, finds one more — and the first census missed it.** `_Avoid_: group agent` under **Resolver** is violated by the same file: `adversarial-review/SKILL.md:66` (*"Each group-agent:"*) and `:69` (*"**Group-agents never invoke `adversarial-review`…**"*), in both mirror copies, name the second-tier reviewer by the name the entry rejects — hyphenated, which is why a grep for the spaced spelling returned only the `_Avoid_:` line. The angle this change ships specifies exactly that search (*"the joined spellings a multi-word term takes as an identifier (`twoWords`, `two_words`, `two-words`)"*); the census did not run it. Those two lines are repaired here on the same grounds and by the same rule. `group-resolution agent` (`:50`, `:79`) is **not** repaired — it is not a name any entry rejects, the drift clause keys strictly off `_Avoid_:` lines, and the tier it names is recorded in ADR-0002 (*"`adversarial-review`'s group-resolution tier"*), which is an immutable record.

The glossary was written as the vocabulary the repo should use, not as a report on the vocabulary it had: `9a8aebb`'s own message names *"interface seams in the design rubric"* while the rubric said `boundary` on two of its three seam bullets, and it added `_Avoid_: group agent` while the file it describes said `group-agent` four times. Both entries were correct; neither sweep happened. That is what makes these repairs rather than concessions.

After both repairs, no shipped text in this repo names a glossary concept by a name its entry rejects, and both new checks are enforceable against this repo with nothing left to find.

**Why this is worth doing rather than tolerating.** The rubric is the *source* of the recurrence, not one instance of it. Measured across this repo's own records:

- **7 of the 8** design docs already committed to `docs/superpowers/specs/` contain at least one Seam-sense `boundary` — **16** occurrences, out of 33 uses of the word. The figure has a mechanical floor: 14 of the 16 are literal echoes of the two rubric bullets, which `git grep -c -i -e 'shared boundary' -e 'shared-boundary' -e 'right boundary'` returns across the eight; the other 2 say the same thing in the author's own words (gh-6's *"Redefined at the boundary means every call site reads the new rule"*, gh-8's *"the same defect — two copies of one fact, kept in sync by memory — at the same boundary"*). The sole exception is `2026-07-22-dev-flow-flatten-design.md`, whose one `boundary` is a stage transition. This document is not in the count: every `boundary` in it quotes the text under repair, quotes the `_Avoid_:` entry, or names a stage transition — see *Applying the pass to this document*.
- **4 of 7** plans do — 5 occurrences, out of 22.

The rule these two figures use, stated so a later document re-derives them instead of copying them: an occurrence counts only where `boundary` names the **Seam** concept — the shared place of a known family where one fix lands so current and future members inherit it. Stage transitions (*"at each artifact boundary"*, *"every stage boundary"*, *"the stop boundaries"*), scope or ownership boundaries (*"issue #7's own stated boundary"*), ordinary wire/storage/version boundary types (*"an ordinary boundary type"*), task boundaries, and diff mechanics (*"hunk boundaries"*) do not count — and they are the majority: 34 of the word's 55 uses across these 15 records. Almost every one that does count is an echo of the rubric's phrasing: "at the shared boundary", "the right boundary", "redefined once, at the shared boundary". The drift clause runs on every design and every plan review. Without the repair it fires, correctly, on essentially every future dev-flow artifact this repo produces, at one resolver group each, forever. Repairing the two lines the authors are copying from dries the recurrence at its source; the clause then catches the residue instead of the pattern.

**Why the entry is not narrowed instead.** Two narrowings were considered and both are worse:

- **Drop `boundary` from `_Avoid_:`.** This records the drift as intended, makes **Seam** an entry whose preferred term the repo's widest-broadcast text does not use, and deletes the only `_Avoid_:` entry in the file with evidence behind it — the one that just found something real.
- **Qualify the entry**, e.g. *"avoid `boundary` for this concept; the repo uses it for a stage transition."* Rejected as the per-instance fix the rubric ranks below a correct-by-default one. `docs/agents/domain.md` already scopes **every** `_Avoid_:` entry to the concept, so qualifying one implies the other two (**Seed**, **Resolver**) are not so scoped, which is false. Where the scoping does need restating is in the check that enforces it, and the shipped clause restates it there — *"only where it names the very concept its entry defines"* — for readers who have not read `domain.md`.

**Does the rubric edit violate "nothing lands in the design rubric"?** No — and because this is the first byte-change to the rubric in three designs, the answer is argued rather than asserted.

**What the precedents ruled.** gh-7 (`:42`, `:241`) and gh-16 (`:38`, `:212`) each report the rubric byte-identical and its nine bullets unchanged. Both sentences sit in those designs' own blast-radius sections — they state where that change landed, not a freeze on the text — and the *rulings* behind them are both rulings on **additions**: gh-7 rejects a rubric bullet because it "pays the widest possible context cost" and "mislocates the work: the rubric states what 'best long-term design' means for a *decider*, and this is an enumeration for a *noticer*"; gh-16 rejects one in the same words. Neither contemplated a correction, because neither had one to make. That ruling is untouched here: this change still adds no check, no bullet and no obligation to the rubric. gh-7 also replaced an already-merged `CLAUDE.md` line (`:256`) on the rubric's "OK to change adjacent code if it gets us to the better design", so correcting merged prose is itself precedented in this lineage.

**The standard this establishes, stated so a successor can hold it to it.** The rubric may be *corrected*, never *extended*, and only when the edit adds no obligation, no concept and no length, and brings a bullet into line with a rule the repo already states elsewhere. Here: `:54` is 54 words before and after, `:58` is 27 before and after, and the rule already stated is `CONTEXT.md`'s **Seam** entry plus `docs/agents/domain.md`'s "don't drift to synonyms the glossary explicitly avoids". An edit failing any clause of that standard is an addition and falls back under gh-7's and gh-16's ruling.

**This is not the measured text being edited to satisfy the measure.** Neither new check reads the rubric: the drift clause reads the *artifact under review*, the angle reads a *diff's added lines*. The rubric is upstream of the vocabulary those artifacts are written in — measurably so, since its own collocations *"the shared boundary"* and *"the right boundary"* appear across eight of this repo's records. Repairing it fixes the source of a recurrence instead of paying for it per artifact, which is what **the rubric's own bullet 3 prescribes**: *"put the fix at the shared seam so current and future members inherit it — a per-instance fix the next person must remember to repeat is a latent regression."* Leaving the two bullets alone makes every future design doc that per-instance fix.

**And the defect is real without any of this machinery.** Bullet 4 says "seams"; bullets 3 and 7 say "boundary"; one concept, one nine-bullet list — visible to a reader with no glossary at all. gh-7 read `:58` as the rubric's existing statement about seams (`:121`) and adopted the term on `codebase-design`'s grounds, which it records as preferring and explicitly defending seam over "boundary" (`:142`); `9a8aebb`'s commit message, which introduced `_Avoid_: boundary`, names "interface seams in the design rubric" in the same breath. The rubric was simply never swept. The new check is how this was found, not why it is being fixed.

**Does `seam` read worse than `boundary` to a resolver in a repo with no glossary?** The objection is real for a skill that ships to other people's repos, and it fails on inspection: bullet 4 already uses "seams" unglossed and gh-7's angle is already called seam placement, so the rubric already assumes a reader who handles the word. The edit removes a synonym; it introduces no term.

**One residue, named rather than hidden.** This repo has an un-glossed concept — the point between two pipeline stages — that it calls "boundary" 27 times, and `CONTEXT.md`'s **Stop** entry uses the word inside its own definition. A reader who has not internalized the concept scoping sees a glossary that rejects a word one of its own entries uses. A **Stage boundary** entry would settle it. It is not added here: no check needs it (the drift clause keys off `_Avoid_:` lines, never off the absence of an entry), the concept scoping already resolves it for any reader of `domain.md`, and adding a glossary entry so that a rejected synonym looks less odd is the glossary growing to serve a reader's confusion rather than the domain. If a future reader trips on it, that is an issue, not a blocker for this one.

## The glossary format this keys off, concretely

`CONTEXT.md` in this repo (67 lines, `0a8a158`) groups entries under `###` headings. An entry is a bolded term line ending in a colon, then one definition paragraph, then optionally an avoided-synonym line:

```text
**Seed**:
A findings-only reviewer in the first tier. It reads and reports; it never edits, judges, or decides.
_Avoid_: finder, first-pass reviewer

**Seam** _(Michael Feathers)_:
A place where behaviour can be altered without editing in that place. This repo uses the word at two levels: ...
_Avoid_: boundary
```

Measured: **17 entries**, **3** of which carry `_Avoid_:`, for **6** avoided synonyms in total (`finder`, `first-pass reviewer`, `group agent`, `judge`, `arbiter`, `boundary`). The optional `_(Michael Feathers)_` attribution parenthetical sits between the term and the colon on one entry.

**Neither piece of shipped text names any of this.** Both say "marks as one to avoid" or "mark as ones to avoid", not `_Avoid_:`. That is deliberate: `adversarial-review` is a general-purpose skill that runs on other people's repos, and `_Avoid_:` is one convention — the one `docs/agents/domain.md` (byte-identical to the upstream `domain-modeling` file) happens to produce. Hardcoding the marker would make both drift checks silently dead in any repo that writes "Not: " or "Deprecated: " instead. A seed reading a glossary can see which line rejects names without being told its exact spelling.

**`CONTEXT-MAP.md` — verified, not assumed.** It does **not** exist in this repo; `find` and `git grep` return it only inside prose. The mechanism is real, not an aspiration: `docs/agents/domain.md` documents it as the multi-context layout ("`CONTEXT-MAP.md` at the repo root if it exists — it points at one `CONTEXT.md` per context"), and #16's shipped pass already names it in exactly this phrasing. This repo is single-context, so in practice both checks read root `CONTEXT.md`.

The glossary-location clause is therefore **byte-identical** rather than paraphrased — `` `CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names `` — in both places it now appears: the pass, where #16 landed it, and the new angle. Two passages × two mirror copies is **4 instances**. Both checks depend on the same fact about where a glossary lives; identical strings make them one greppable fact, and a future change to the glossary convention edits identical spans instead of hunting a paraphrase.

**The asserted span stops short of the delimiters, and that is deliberate rather than sloppy.** The pass parenthesizes the clause (`read the domain glossary first (…);`) while the angle sets it off with an em dash (`a domain glossary — …`), because the two sentences around it are different sentences. Asserting the parenthesized form would return 2 on a correct tree and silently prove nothing about the angle. Verification step 7 greps the unparenthesized span, which is the part that has to stay in step.

## The open question, answered

> *"the check has no fallback … the angle is a silent no-op in most repos … Worth confirming that a no-op angle still earns its ~150 tokens in the widest-broadcast diff prompt."*

**Answer: it earns its place. Ship it.** Two parts of the question's premise need correcting first, and one part of it is right and worth naming.

**"Widest-broadcast" is the wrong label for the angle's slot.** `CONTEXT.md` reserves that phrase for the **design rubric**, which ships into every resolver in all three modes *and* the design/plan quality seed. The angles block is carried by exactly one prompt — the `diff`-mode quality seed — plus the orchestrator's single whole-file load. That is *narrower* broadcast than #16's pass, which the correctness seed carries in two modes. The measured figure for the whole change: **371 words** (~520 tokens) added to a 2,472-word file, ~15.0% of the file, and against gh-7's real review invocation of 484,005 tokens the growth is roughly **0.107%** — versus 86,022 tokens for one false-positive resolver group, ~165×. The ratio gh-7 established is not close.

**"Silent no-op in most repos" is the established shape of every gated check in this file, not a defect unique to this one.** Seam placement (200 words) is a no-op on every diff adding no bridge construct, which is most diffs. Input-contract completeness (114 words) is a no-op on every artifact accepting no new outside input. Terminology collision was a no-op on every artifact coining no term. A frequency-of-firing bar would retroactively disqualify all three, including both of gh-7's families.

**The part that is right, and does need stating:** the glossary trigger is a property of the **repo**, not of the artifact, and it now gates two checks rather than one. The other three fire or not per-artifact; this one is either always-on or never-on for a given repo. In a repo with no glossary the angle is permanently dead weight rather than occasionally dead, and the drift clause with it. That is a genuinely different failure shape and #20 is correct to flag it.

It still wins, on four counts:

1. **The cost is ~520 tokens, paid at most twice per review.** There is no competing use for them; skill context here is not a rationed budget, and the comparison that governs is against the 86k-token FP group, not against zero.
2. **The trigger is cheap to fail, and now fails once for both checks.** One file read. A seed in a glossary-less repo reads one sentence, finds nothing to iterate, and stops — it does not grep, judge, or report. The drift clause routes to the same no-op through the same sentence.
3. **The repo that ships this has a glossary.** Every dev-flow review of these plugins fires the trigger, on artifacts and diffs to the very prose the glossary defines. The "most repos" denominator excludes the case where the check's own maintenance happens.
4. **The alternative that would make the no-op cost literally zero is worse.** See *Conditional prompt assembly*, below.

**The design must state the no-op rather than let it be discovered**, which #20 asks for and which both pieces of shipped text do in their last clause. The condition is closed by construction rather than enumerated: a missing file, an empty one, a file that is not a glossary, a glossary with no rejected names, and a `CONTEXT-MAP.md` path that does not resolve all yield nothing to iterate and all route to the same silent stop. Those sentences also carry the never-flag rule; see *Why the never-flag clause is restated*.

**What would change the answer.** If a future change makes the `diff` quality seed carry the design rubric as well, or if the angles list grows past roughly eight with several repo-level triggers among them, the right response is to restructure — gate the repo-level checks once as a group — not to delete one. That threshold is stated so a future reader has a rule rather than a re-litigation.

## Why the never-flag clause is restated rather than shared

#16's pass ends *"the glossary's own state is never a finding: never flag it, never propose creating one."* The new angle restates that rule verbatim, and the pass keeps its own copy. The rubric says to prefer the shared seam over a per-instance fix, so the restatement needs a reason.

There is no shared seam available that costs less than the restatement. The two checks live in different table rows, different seeds, and different modes; the `diff` quality seed prompt never contains the pass's text. Without the clause, a `diff`-mode seed in a glossary-less repo has every incentive to report the absent glossary as the finding — which is the pipeline's worst outcome per token, since the "finding" is unfixable by a review that is forbidden to write repo state. Inventing a shared "rules common to glossary-reading checks" section to hold one sentence would cost more prose than it saves and would be read by seeds that need only one of the two checks.

**The instance count is not what decides this, and this design should not lean on it.** After this ships, two checks carry the sentence, and the rubric's *"widen the lens only against concrete demand (planned siblings, 2+ instances)"* treats two as concrete demand rather than speculation — so the count is met, not pending. What the same bullet asks next is where the shared seam is, since *"zooming out finds the right seam, it doesn't add layers"*, and here there is none to find. Each seed prompt is assembled from the sections its mode names and must be self-contained by the time it reaches a subagent; a "rules common to glossary-reading checks" section, in a file whose sections are cherry-picked into prompts, is not a seam but an indirection the prompt-builder has to remember to resolve for two of the three modes — the *"each caller must remember a flag, ordering, or manual step"* shape the rubric ranks below a correct-by-default one. Restating in place is the correct-by-default option: the check that reads a glossary carries the rule that governs glossary reading, with no assembly step to forget.

**What changes the answer is a seam appearing, not a count rising.** If prompt assembly ever gains a block both seeds include — the machinery *Conditional prompt assembly* rejects for the trigger — the sentence moves there. Until then the duplication is managed by making it byte-identical rather than paraphrased, and the same treatment is now given to two more spans this change duplicates: the glossary-location clause and the naming discriminator. One `git grep -F` finds each as a single fact, and a future change edits identical spans instead of hunting a paraphrase. Verification asserts all three counts, because these duplications live twice inside one file and `check-sync.py` only ever proves the two mirror copies agree with *each other*.

## Applying the pass — as this change ships it — to this document

The check this change ships, both halves, run against the document that specifies it.

### Collision half

- **`glossary conformance`** (coined here). `conformance` already ships in this repo's prose twice: `CONTEXT.md`'s **Provenance** entry ("Evidence of fan-out and tier conformance") and ADR-0001's "design-conformance" (`docs/adr/0001-duplicate-the-two-dev-flow-variants.md:9`; the rule it names lives in `CLAUDE.md`, which states it without using the word). Both mean *"X matches the standard it is supposed to match"*, which is exactly the sense here. Same sense; **no finding**.
- **`collision`** — used above for *"one word carrying two senses"*, and **not coined here**: `adversarial-review/SKILL.md` already ships that sense verbatim (*"**Against itself:** one word carrying two senses, or two words carrying one"*), so this document adopts the shipped word for the shipped concept. The pipeline pair's *"accidental branch collisions"* and *"Intake collision check"* are the ordinary computing sense — one identifier, two claimants — applied to branch names rather than words. Same sense, different domain; **no finding**. Renaming would be the actual error, leaving one concept with two names across the pass and this document.
- **`drift`** — now a *shipped* name for a failure class, so it is re-checked rather than inherited. The repo uses the word for `check-sync.py`'s "mechanical drift check", ADR-0001's hand-mirrored divergence (*"We control the resulting drift mechanically where the file structure allows and by hand where it does not"*), and the plan seed's "drift from the design doc" (`SKILL.md:30`, two rows above the pass in the same table). All mean *two things that should agree diverging*; terminology drift is that relation applied to names, exactly as branch collision is collision applied to refs. `docs/agents/domain.md` already applies it to names in exactly that way — *"Don't drift to synonyms the glossary explicitly avoids"* — so this document adopts the repo's own word for the concept rather than coining one. The compound headings (`Terminology collision and drift`, "drift from the design doc") keep the two unambiguous where they are adjacent. **No finding.**
- **`naming use`** (coined here) — no prior use anywhere in the repo. **No finding.**
- **`terminology collision`** — **fired during the #20-only draft, and the design changed because of it.** `CONTEXT.md` does not define it, but the pass shipped it as the name of a specific `design`/`plan` correctness check. Naming the new angle "terminology collision" too would have put one name on two checks with different mechanisms in the same file. That is why the angle is called **glossary conformance**. This change retires the tension from the other side as well: after the rename, "terminology collision" is a failure class rather than a pass name.
- **`angle`**, **`trigger`**, **`reportability rule`**, **`seed`**, **`resolver`**, **`pass`**, **`artifact`** — each used throughout in `CONTEXT.md`'s sense, checked by holding each fixed across the whole document. In particular `pass` appears here only for the named check, never in the ordinary-English "a run over a document" sense that #16's own review had to correct.

**Against itself:** no word carries two senses; `collision` and `drift` are explicitly separated in *The avoided-synonym half* precisely so they cannot.

### Drift half

Run over all six names `CONTEXT.md` marks as ones to avoid:

- **`finder`**, **`first-pass reviewer`**, **`arbiter`** — zero occurrences in this document. **No finding.**
- **`group agent`** — 13 occurrences, spaced and hyphenated, and every one is a *mention*: the `_Avoid_:` entry being quoted (the glossary-format section, the six-name enumeration, the repair argument), the two `SKILL.md` lines this change repairs being quoted or replaced, and the greps that search for them. This document's own name for the second tier is **resolver** throughout — "the resolvers' call", "one resolver group each", "group resolvers". Excluded by the mention-versus-use sentence, on exactly the grounds `boundary` is. **No finding** — which is the point: the same clause that keeps this document clean is what let the repair be found in `SKILL.md`, where the uses are real.
- **`judge`** — appears only as a verb ("judging the group's findings", "a comparison, not an invention"). Names nothing. **No finding.**
- **`boundary`** — appears throughout, and every occurrence is one of three kinds: a quotation of the shipped text this change repairs (including the residue and blast-radius greps that search for that exact string), a quotation of the `_Avoid_:` entry itself, or the stage-transition sense ("at each artifact boundary", "stage boundary"). Each kind is excluded by a clause the pass actually ships — the first two by the mention-versus-use sentence, the third by *"only where it names the very concept its entry defines"* — rather than by a hand-sort this document performs and the seed cannot repeat. Measured: **28** Seam-sense occurrences on **15** lines, of which 11 are grep patterns this document's own verification and blast-radius steps search for, and 17 are quotations — of the rubric, of `0a8a158`, of #16's review, or of the records the census cites by name. **This document never names the Seam concept `boundary` in its own voice** — it says "seam", including where it quotes the rubric bullets in their repaired form. **No finding**, and the check was run rather than assumed: `Does CONTEXT.md's _Avoid_: boundary entry survive` exists because this half was applied here first.

## No tier name appears in the new text

gh-7 recorded a **standing obligation**: every future tier or protocol change must keep each added check coherent, "which is why neither pass restates a tier name", and #16 repeated it ("the pass names no tier"). Concretely, the Model section is the single place that says which model class seeds and resolvers run on; the #14 swap had to sweep every restatement of that fact, and each restatement is a place the sweep can miss.

Every piece of text this change adds or edits was checked against that: the angle, the drift clause, the renamed heading, the two table cells, the two rubric bullets, and the two Resolution-procedure lines contain no `sonnet`, no `opus`, and no "seed model". The two Resolution-procedure lines are the only edit that touches the section describing the tiers at all, and they introduce nothing but the **role** name `resolver` — the word `CONTEXT.md`'s entry already prefers, and the word the same line already uses in "group resolvers" one clause later. That line's existing *"the protocol has exactly two tiers (seed reviewers, group resolvers)"* is carried through byte-identically: it states a **count and two role names**, never a model class, so it is not the restatement gh-7's obligation is about, and this change does not add, remove or reword it. Both checks say "the fix is the resolvers' call" — a **role** name, identical to the phrasing the existing passes use, and unaffected by any tier change. The rubric edit is the one that would matter most if it were wrong, since the rubric reaches every resolver in all three modes; it changes two nouns and touches no statement about models. The obligation is honoured.

## Rejected alternatives

**A diff-side trigger restricted to exported/public names.** The strongest alternative for the #20 half, and the one #20's "Sketch" section is arguing against. Rejected on four counts, the third of which is decisive:

1. *The bound is not actually small.* One new module can export 20+ names and a feature-sized diff many more, against a fixed 23 literal searches here. The count also grows with diff size, which is the property the inversion exists to remove.
2. *"Exported/public" is not language-uniform.* Python has no keyword (a leading-underscore convention), Go uses capitalization, Rust `pub`, TypeScript `export`. A seed applying "public" across a polyglot diff is applying four different rules it has to infer.
3. **The repo this ships from is markdown.** `SKILL.md` prose has no notion of an export, so the trigger would not fire at all on the diffs that motivated this issue — the ones that edit `adversarial-review`'s own vocabulary. An alternative that is inert on the primary case loses to one that is not.
4. *The false-positive economics are the ones #20 already priced.* Each exported name needs a repo-wide grep to establish a colliding sense, and `config`, `client`, `handler`, `result` always hit. That is the 86k-token path.

It does buy one thing the chosen approach does not: an execution-time name colliding with a **non-glossary** shipped-prose sense. That is hole 2's residue, named in *The gap, restated*. It is not worth 86k tokens a group.

**Extend the existing seam-placement angle instead of adding a sixth.** Rejected. The two share nothing: seam placement's trigger is a structural property of a construct the diff adds, and it "proposes removals, never a restructuring" — a terminology finding proposes neither a removal nor a relocation. Merging them produces one paragraph with two unrelated triggers, which is exactly the degradation #16 refused when it declined to bolt a diff trigger onto its own pass. #20's constraint says sixth angle for this reason, and inspection agrees.

**A third `diff`-mode seed, or a separate "vocabulary" seed.** Rejected, on #16's grounds unchanged: it raises `diff` seed cost by 50% for one question and breaks the uniform two-seed shape the whole Seed passes section and the provenance line (`seeds: N× <tier>`) are written around. The design/plan-side version of the same idea is rejected in *The #22 half — the alternatives rejected*.

**Extend the `diff` correctness seed.** Not available. The pinned `code-reviewer.md` is used "as designed", with only four placeholders filled. Adding a terminology item means either unpinning the template — losing the property that makes it trustworthy and inheriting maintenance of an upstream file — or smuggling instructions through `[DESCRIPTION]`, which is not what that placeholder is. #20 states this and it holds.

**Conditional prompt assembly — omit the angle and the drift clause when no glossary exists.** Rejected, though it is the only option that drives the no-op cost to literally zero. It moves a trigger the seed evaluates in one read into the orchestrator's prompt-building step, where nothing else is conditional; it makes the angles-block header's "all six apply" false in the omitting case, so the header has to say "five or six"; it makes the angle count vary between two runs of the same skill, which the `CONTEXT.md` **Angle** entry and any future provenance-style check would then have to accommodate; and it saves nothing on the orchestrator's whole-file load, which is paid either way. It trades a fixed ~520 tokens for a variable-shape prompt in two modes rather than one. The rubric's "a fix must be worth its complexity" settles it.

**Also grep the repo for non-glossary senses in the `diff` angle, as #16's collision half does.** Rejected. That is the exact cost #20 prices at ~86k tokens per false-positive group, and it re-imports the unbounded candidate set the inversion was designed to eliminate. The glossary is the whole bound for the angle; that is the trade, and the residue is named rather than hidden.

**Gate the review on a glossary existing.** Rejected, on #16's grounds unchanged: a shipped general-purpose skill must not assume one documentation convention, and turning a missing file into a halt is the pipeline's most expensive outcome.

**Leave the rubric's two `boundary` bullets alone and let the drift clause report them.** Rejected — this is the option the #20-only draft implicitly took by ruling the glossary out of scope. Measured cost: 7 of the 8 existing design docs and 4 of 7 plans carry Seam-sense `boundary` — 21 occurrences across 11 of the 15 committed records — nearly all of it copied from those two bullets, and the drift clause runs on every design and plan review. That is a correct finding recurring on essentially every future artifact, at one resolver group each, in exchange for not changing two words.

**Repair the 32 Seam-sense `boundary` occurrences in `docs/superpowers/` records too.** Rejected. Records are history; the pass reads the artifact *under review*, and a merged record is never that again. The angle never searches them either. Rewriting them would be a large diff whose only effect is on text no check reads.

**Narrow or drop `CONTEXT.md`'s `_Avoid_: boundary` entry.** Rejected, with the evidence, in its own section above.

## Honest limit of the discriminator

The naming discriminator is a semantic judgment and can be applied too loosely. The #20-only draft named its worst case as the design rubric's *"put the fix at the shared boundary"* and *"zooming out finds the right boundary"*, and argued only that the damage was bounded. **This change repairs that worst case instead**, so it is no longer the shipped-text exposure; what replaces it is strictly easier to judge.

**What is left in shipped text.** After the repair, all 27 live `boundary` occurrences name a stage transition. Excluding them needs no judgment about whether a phrase is a "naming use" — it needs only the comparison the clause actually asks for, against a definition read one step earlier. That is the easiest case the discriminator ever faces, not the hardest.

**What is left as a class.** A future artifact or diff writing "the shared boundary" on its own initiative. It is now caught in both places it can appear: artifact-side at the design or plan stage by the drift clause, where it is actionable and cheap, and in shipped text at merge time by the angle. Neither catches a design/plan *record* re-adding the phrase inside a `diff` — deliberately, per the scope clause, and that is now the residue rather than the main case.

**The bound that was claimed and is real.** Measured on `0a8a158`: 985 of 996 added lines were under `docs/superpowers/`, all five of that change's `boundary` additions were among them — one of them literally *"the fix belongs at the shared boundary"* — and its 11 added lines of shipped text contained no avoided synonym. Added-lines-only bounds what is left: unchanged prose produces nothing unless a diff re-adds it.

**What is not a bound is the reportability rule**, and an earlier draft of this design claimed it was. It screens a reader who cannot say what the artifact's sense *is*; it does not screen an articulable case. A reader who calls *"the shared boundary"* a naming use can quote **Seam**'s definition, quote the use, give a `file:line`, and satisfy the rule in full. So the residue is priced rather than argued away: a defensible drift finding can reach a resolver and cost one group. That is the trade gh-7 already accepted for seam placement — *"budget one resolver group on that fraction of PRs"* — not a claim the rate is zero. What this change does is remove the one instance that made the rate non-hypothetical.

Success criterion for a future run, stated so it can be checked: a reported finding must quote the glossary entry, the artifact's or diff's use, and a location. A run that reports "several identifiers overlap glossary terms" without those three is evidence the reportability rule is too weak to have shipped.

## Context cost

`adversarial-review/SKILL.md` is 2,472 words today. The addition is:

| Edit | Words |
|---|---|
| Glossary-conformance angle (new) | +241 |
| Terminology pass, 217 → 345 | +128 |
| `diff` row's quality cell | +2 |
| `design` row's correctness cell | +1 |
| Angles-block header | −1 |
| Rubric bullets 3 and 7 | 0 |
| Resolution procedure, lines 66 and 69 | 0 |
| **Total** | **+371** |

That is about **15.0%** of the file, ~520 tokens, taking it to 2,843 words. The angle is carried by the orchestrator's one whole-file load and by the `diff`-mode quality seed prompt. The pass is carried by that same whole-file load and by the `design`- and `plan`-mode correctness seed prompts — two modes, so it is the more expensive half per pipeline run, as *What it costs per run* prices.

After this change the pass is the longest single passage in the file at 345 words, ahead of the new angle at 241 and seam placement at 200. It is not a new order of magnitude, but it is now 1.4× the next-longest passage, which is why *The alternatives rejected* states a threshold for splitting it rather than leaving that to a future re-litigation. The 128 words it gains are the hoisted glossary read, the `**Collision**` scoping prefix, the drift trigger, the byte-identical discriminator, the hyphenated-spelling clause, the mention-versus-use exclusion, and the drift arm of the reportability rule — the last three being the clauses that carry the false-positive load, which is where this file has consistently chosen to spend words.

Measured against gh-7's real review invocation of 484,005 tokens, the growth is roughly **0.107%**. One false-positive resolver group measured 86,022 tokens, ~165× the entire addition. Every word spent on the triggers, the naming discriminator, and the reportability rules is therefore lopsidedly worth it, which is why all of them are stated in full.

Per-clause marginal value was run over both pieces and nothing was cut. The weakest survivors keep their stated reasons: *"never the diff's names"* is the whole inversion in three words and prevents a seed from helpfully expanding the iteration; the discriminator sentence is what keeps `pass`, `stop`, `artifact`, `judge` and `boundary` from flooding either check, and it is the difference between this design and the one #20 rejects. Two candidate clauses **were** cut during drafting — a standalone sentence restating the collision/drift distinction inside the pass (24 words; the two labelled triggers already carry it, exactly as the angle's single candidacy sentence does) and a second negative example in the reportability rule (10 words; the trigger is six fixed names, so the vocabulary-audit failure it guarded against is not reachable).

## Exact change list

Five files. Every wording below is literal.

### 1 & 2. `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`

A declared `check-sync.py` mirror pair. **Every edit below lands byte-identically in both files.** None of the new or edited text contains a `dev-flow` or `dev-flow-worktree` token, so the two copies compare equal in every touched region before canonicalization does anything. Verified: lines 28, 29, 34, 46, 54 and 58 are already identical between the two copies today.

Nine edits: eight in-place line replacements and one two-line insertion. Line numbers are the current (pre-change) file, which is **87 lines**. The insertion goes after line 40, so the replacements at 46, 54, 58, 66 and 69 are at 48, 56, 60, 68 and 71 afterwards; apply the replacements by content match, never by number, and the order does not matter.

#### Line 28 — Seed passes table, the `diff` row

The quality cell names the angles the seed runs; a sixth is added, so the cell must name it or a prompt-builder resolving the cell ships five. Only the quality cell changes; the correctness cell is byte-identical to today. Replace the whole line with:

```
| **diff** | `/simplify`'s four angles plus this skill's seam-placement and glossary-conformance angles, inlined (below), findings-only, run against `BASE..HEAD`. | The superpowers `code-reviewer.md` template, used as designed (already read-only/findings-only) — see "Pinned template," below. |
```

#### Line 29 — Seed passes table, the `design` row

The correctness cell names the pass, which is renamed. Only the last clause changes. Replace the whole line with:

```
| **design** | The design rubric (below) *is* the lens, applied adversarially to the proposed approach. | A prose-integrity checklist: placeholders/TBDs, internal contradictions, planning-blocking ambiguity, unstated assumptions, missing or untestable success criteria — plus the input-contract completeness and terminology collision-and-drift passes (below). |
```

**Line 30 (the `plan` row) is not edited.** It refers to "the prose checklist above" and names no pass, so the rename does not reach it.

#### Line 34 — the angles-block header

`five` → `six`, and `a fifth` → `two`, keeping "(verbatim)" scoped to the four `/simplify` bullets it describes. Replace the whole line with:

```
**The four `/simplify` angles (verbatim), then two of this skill's own — all six apply:**
```

#### Insert after line 40 (the `Seam placement` paragraph) — the sixth angle

Insert exactly two lines: one empty line, then this line. Placing it after seam placement and before the `Pinned template` paragraph keeps this skill's two own angles contiguous under the header that introduces them, and keeps the `diff`-mode angles ahead of the two `design`/`plan` notes that close the section — the layout gh-7 established and gh-16 preserved.

```

**Glossary conformance:** applies only where the repo has a domain glossary — `CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names. Iterate the glossary's entries, never the diff's names: for each term, and for each synonym its entry marks as one to avoid, grep the diff's added lines of shipped text for that term — case-insensitively, and in the joined spellings a multi-word term takes as an identifier (`twoWords`, `two_words`, `two-words`); skip design/plan records (`docs/superpowers/`), which discuss the vocabulary rather than ship it. A hit is a candidate only where the diff uses the term as a **name** — an identifier, a field, a type, a user-facing or logged string, or prose that labels a concept — and then only if it names something the entry does not define, or reintroduces an avoided synonym for the very concept the entry does. The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate. Report only what you can quote: the glossary's sense, the diff's sense, and the `file:line` where the diff's sense lives; "this name is confusing" is not a finding. Findings only — a mismatch does not imply a rename, so report it either way; the fix is the resolvers' call. Where the glossary yields no entries to iterate this angle reports nothing: proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one.
```

#### Line 46 — the terminology pass, renamed and extended

Every sentence #16 shipped survives; the glossary read moves to the front so both halves share it, the existing trigger gains a `**Collision**` prefix, and the `**Drift**` clause and its arm of the reportability rule are added. Replace the whole line with:

```
**Terminology collision and drift — the design *and* plan correctness seed:** read the domain glossary first (`CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names); both halves key off it. **Collision** applies only to words the artifact introduces or adopts as the name of a concept — one it defines, coins, or borrows from another source — never to the repo's vocabulary at large, and never to a word the artifact uses in the sense the repo already has. For each, check twice. **Against the repo:** grep the review's working directory for any term the glossary does not settle — a sense that lives only in shipped prose is still a collision. Grep shipped prose only: skip the artifact itself, and skip prior design/plan records (`docs/superpowers/`) — history, not shipped text. **Against itself:** one word carrying two senses, or two words carrying one. **Drift** is the inverse and applies only to the names the glossary's entries mark as ones to avoid: search the artifact for each such term, spaced or hyphenated as prose compounds it, and count a hit only where it names the very concept its entry defines. The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate. Count only the artifact's own *use* of a name; a term it merely *mentions* — quoting the glossary, quoting or describing text it proposes to change, reporting a prior record's wording — is not a candidate. Report only what you can quote: for a collision, the artifact's sense, the colliding sense, and where the colliding one lives; for drift, the entry's preferred term, the artifact's use, and where it lives. "Define your terms" is not a finding. Findings only — neither a collision nor drift implies a rename, so report it either way; the fix is the resolvers' call. If the glossary is missing, settles nothing about the term, or marks no names to avoid, grep and proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one.
```

#### Line 54 — design rubric, bullet 3

One word: `boundary` → `seam`. Replace the whole line with:

```
- Before fixing at the point of failure, zoom out one level: if the thing touched is one of a known family (connectors, handlers, jobs…), put the fix at the shared seam so current and future members inherit it — a per-instance fix the next person must remember to repeat is a latent regression.
```

#### Line 58 — design rubric, bullet 7

One word: `boundary` → `seam`. Replace the whole line with:

```
- Value simplicity; widen the lens only against concrete demand (planned siblings, 2+ instances), never speculation — zooming out finds the right seam, it doesn't add layers.
```

#### Line 66 — Resolution procedure, step 3

One word: `group-agent` → `resolver`, the name `CONTEXT.md`'s **Resolver** entry marks as one to avoid. Replace the whole line with:

```
3. Each resolver:
```

#### Line 69 — Resolution procedure, the no-recursion clause

One word: `Group-agents` → `Resolvers`, the same entry on the same grounds. Nothing else on the line changes. Replace the whole line with:

```
   - Performs an **inline** adversarial self-check within its own context — it tries to break its own conclusion (counterexamples, simpler alternatives, hidden coupling) before concluding. **Resolvers never invoke `adversarial-review` or spawn further reviewer agents** — the protocol has exactly two tiers (seed reviewers, group resolvers), and recursion is forbidden.
```

#### Resulting file shape

Both copies go from **87 to 89 lines**.

| Line | Content |
|---|---|
| 26–27 | table header, unchanged |
| **28** | `diff` row — **replaced** |
| **29** | `design` row — **replaced** |
| 30 | `plan` row, unchanged |
| 31 | blank |
| 32 | `Do NOT invoke the /simplify skill …`, unchanged |
| 33 | blank |
| **34** | angles-block header — **replaced** |
| 35–38 | the four `/simplify` bullets, unchanged |
| 39 | blank |
| 40 | `**Seam placement:** …`, unchanged |
| **41** | blank — **inserted** |
| **42** | `**Glossary conformance:** …` — **inserted** |
| 43 | blank |
| 44 | `**Pinned template for diff / correctness:** …` (was 42) |
| 45 | blank |
| 46 | `**Input-contract completeness — …` (was 44) |
| 47 | blank |
| **48** | `**Terminology collision and drift — …` (was 46) — **replaced** |
| 49 | blank |
| 50 | `## The design rubric` (was 48) |
| **56** | rubric bullet 3 (was 54) — **replaced** |
| **60** | rubric bullet 7 (was 58) — **replaced** |
| **68** | Resolution procedure, step 3 (was 66) — **replaced** |
| **71** | Resolution procedure, the no-recursion clause (was 69) — **replaced** |

### 3. `CONTEXT.md` — the glossary entry this change makes true

The **Angle** entry enumerates its instances, unlike **Pass**, so it goes stale the moment a sixth ships. `docs/agents/domain.md` has every skill read the glossary before exploring, so a stale enumeration sends an agent looking for a five-item list that no longer exists.

**The glossary changes with the thing it defines** — gh-7's ruling, which put its own `Angle` entry in the commit that shipped seam placement rather than in a follow-up. Same here.

Replace **line 30** (the definition line under `**Angle**:`) with:

```
One lens in the diff-mode quality seed's list: reuse, simplification, efficiency, altitude, seam placement, glossary conformance.
```

`CONTEXT.md` stays at **67 lines** — a one-line replacement, not an append. It ships into no plugin and `check-sync.py` never reads it.

**No other `CONTEXT.md` line changes, and that is a decision rather than an omission.** The **Seam** entry and its `_Avoid_: boundary` line are kept byte-identical, for the reasons in *Does `CONTEXT.md`'s `_Avoid_: boundary` entry survive a check that enforces it?*. The **Pass** entry is not edited: it defines the shape, not the instances, which is exactly why it does not go stale when a pass gains a clause. The **Design rubric** entry still reads "nine-bullet", which is still true. No new entry is added — **Pass**, **Trigger** and **Reportability rule** already define the shape both new checks are instances of, and adding an entry per check is the glossary growing a row per line of `SKILL.md`.

### 4 & 5. Version bumps

The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so a skill edit at an unchanged version is never picked up on re-sync.

| File | From | To |
|---|---|---|
| `plugins/dev-flow/.claude-plugin/plugin.json` | `2.5.0` | **`2.6.0`** |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `1.7.0` | **`1.8.0`** |

Both current versions were read from the manifests, not assumed. Minor in both, and still minor with #22 folded in: the invocation signature, the contract, the provenance format, the mode set, and the model policy are all unchanged. Same bump shape as gh-7 (`2.3.0`→`2.4.0`, `1.5.0`→`1.6.0`) and gh-16 (`2.4.0`→`2.5.0`, `1.6.0`→`1.7.0`).

Neither `description` changes, so `.claude-plugin/marketplace.json` is not touched.

## Sync constraint — how `check-sync.py` still passes

**Check B (mirror pair `adversarial-review`)** requires the two files to be line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, except the declared exception at line 12.

1. **All nine edits land in both files.** A one-sided edit produces an undeclared-divergence failure naming the line.
2. **The insertion is symmetric, so line counts stay equal.** Both files go 87 → 89. An asymmetric insertion is a `LINE_COUNT_FIX` failure and could not be declared as an exception even deliberately — the schema declares only same-index, one-line-for-one-line divergences.
3. **No new variant token is introduced.** Verified: the added and edited text contains no `dev-flow` or `dev-flow-worktree` occurrence.
4. **The declared exception still fires and does not go stale.** It covers line 12, above every edit, which does not shift.

**Check A (manifest descriptions)** compares `name`, `source`, and `description` between each `plugin.json` and its marketplace entry, and does not read `version`. This change edits only `version`, so `marketplace.json` is not touched and Check A is unaffected.

**No hand-mirrored file is edited.** Both pipeline `SKILL.md` copies and both `README.md`s are untouched (see *Blast radius*), so the pair with no mechanical check behind it stays out of this change entirely.

## Blast radius

Two searches, each stated because they cover different edits.

**The angles block and the rubric's own vocabulary.** A repo-wide search of tracked files outside `docs/superpowers/`:

```sh
git grep -n -w -i -e angle -e angles -e simplify -e 'quality seed' -- . ':!docs/superpowers/'
```

Hits **only** in the two `adversarial-review/SKILL.md` copies and `CONTEXT.md`. `-w` is load-bearing here, not tidiness: without it `angle` matches `mangled` in `CLAUDE.md:9` — *"text mangled identically in both sides passes it"* — and the **only** claim is false. That is precisely the substring-inside-an-unrelated-word false positive the naming discriminator exists to survive (`pass` in a Python stub, `artifact` in a CI diff), turning up in this document's own scope check; `angle` is the first bare common word this formula has been pointed at, which is why gh-7's and gh-16's substring searches were sound and this one is not. `-e angles` is redundant today — every plural line also carries `/simplify` or `quality seed` — and is stated anyway, because a future *"the six angles"* line would carry neither, and a blast-radius search that misses one is a silent scope error. **Do not carry `-w` forward as a house rule:** it is chosen per pattern, and it would break gh-7's `seed pass`, which matches only as a substring of *"Seed passes"*.

**The pass name and the rubric's two repaired lines.** `-w` is deliberately *not* used here, because `terminology-collision` must match inside a hyphenated compound:

```sh
git grep -n -i -e terminolog -e 'shared boundary' -e 'shared-boundary' -e 'right boundary' -- . ':!docs/superpowers/'
```

Hits **only** at `adversarial-review/SKILL.md:29` and `:46` (the two lines this change replaces) and `:54`/`:58`, in both copies. Nothing outside the mirror pair names the pass or quotes the rubric.

Specifically confirmed:

- **`plugins/dev-flow/skills/dev-flow/SKILL.md`** and **`plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`** — **zero hits** for either search. They invoke the review by mode and delegate seed content entirely; neither enumerates an angle or names a pass. The hand-mirrored pair stays out of this change. Both do use `boundary` for stage transitions (9 and 5 occurrences), which is the sense the drift clause does not reach and which is left alone.
- **Both `README.md` files** — **zero hits** for either search. Their four `boundary` occurrences each are stage transitions ("at each artifact boundary", "every stage boundary"), untouched.
- **`.claude-plugin/marketplace.json`** and both `plugin.json` descriptions — carry "at each artifact boundary", the stage-transition sense. No `description` change; Check A does not read `version`.
- **`CONTEXT.md`** — the **Angle** entry only. Its two `boundary` occurrences (**Stop**'s definition and **Seam**'s `_Avoid_:` line) are deliberately left byte-identical; see the glossary section.
- **The `Working directory` section of the mirror pair** — **not edited, and this is load-bearing.** The angle is the fourth read-only reviewer needing the repo root, after both `diff`-mode seeds and the terminology pass. The sentence #16 landed at the shared seam — *"Read-only reviewers receive that root as well as absolute paths for every file the review hands them"* — already covers it, and covers the drift clause's artifact read too. That is the shared-seam fix paying off exactly as the rubric predicts: the per-instance alternative would have needed a restatement here, and now a second one.
- **`CLAUDE.md`** — untouched. The mirrored-pair verification rule gh-7 landed already covers this change as written (residue grep plus a per-change conformance script), and this change is exactly the case it describes.
- **`docs/agents/domain.md`** — untouched, and load-bearing unmodified: its *"Don't drift to synonyms the glossary explicitly avoids"* rule is the specification the drift clause enforces, and its concept scoping ("when your output **names a domain concept**") is what the clause's *"for the very concept its entry defines"* restates for readers who have not read it.
- **`docs/adr/`** — untouched. ADRs record decisions, not vocabulary; both checks read the glossary only. ADR-0001 and ADR-0002 contain no `boundary` and no rubric quotation.
- **`scripts/check-sync.py`**, **`.github/workflows/`** — untouched.

## Verification

1. `python3 scripts/check-sync.py` — passes. Expect `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`.
2. `claude plugin validate .` — passes; the 8 missing-author warnings are expected.
3. **Residue grep (always, per `CLAUDE.md`).** All nine return **no hits**:

   ```sh
   git grep -n -F -e 'seam-placement angle, inlined' \
                  -e "then a fifth of this skill" \
                  -e 'altitude, seam placement.' \
                  -e 'and terminology-collision passes' \
                  -e '**Terminology collision — the design' \
                  -e 'put the fix at the shared boundary' \
                  -e 'finds the right boundary' \
                  -e 'Each group-agent:' \
                  -e 'Group-agents never invoke' -- plugins/ CONTEXT.md
   ```

   Every one is text this change deletes: eight are the in-place replacements in the mirror pair (2 hits each today, one per copy), the third is `CONTEXT.md`'s stale five-item enumeration (1 hit today). A surviving hit on any mirror-pair string means one side was missed — the failure `check-sync.py` catches only if the *other* side changed. The pathspec is required: this design quotes all nine strings in prose, and `docs/superpowers/` must not be searched.
4. **The Seam-sense repair is complete.** The mechanical form of the glossary decision — after this change no shipped text names the **Seam** concept by the name `CONTEXT.md` rejects. Expect **no hits**:

   ```sh
   git grep -n -i -e 'shared boundary' -e 'shared-boundary' -e 'right boundary' -- . ':!docs/superpowers/'
   ```

   This is broader than step 3's exact strings on purpose: it also fails if a fixer "helpfully" reflows one of the two rubric bullets while keeping the word. Every remaining `boundary` in shipped text — 27 occurrences — must be the stage-transition sense, which this search does not match.

   The companion check for the second repair, in the same broader-than-step-3 form. Expect **exactly one hit**, `CONTEXT.md:15` — the `_Avoid_:` line, which the never-flag clause puts outside every finding:

   ```sh
   git grep -n -i -e 'group.agent' -- . ':!docs/superpowers/'
   ```

   Today it returns **5**: that one line plus `SKILL.md:66` and `:69` in both mirror copies — measured, not assumed. `-i` and the `.` wildcard are load-bearing: they are what the spaced-spelling grep that produced the first census lacked. `group-resolution agent` (`:50`, `:79`) does not match this pattern and is deliberately not repaired; see the section above.
5. **Design conformance — all ten blocks landed verbatim, in the right place.** This is the step steps 1–4 structurally cannot provide. Step 3's residue grep is tied to the in-place replacements and says nothing about the insertion, and `check-sync.py` compares the two mirror copies only to *each other*, so a word mangled identically in both passes it at the correct 89 lines — and it never reads `CONTEXT.md` at all. This check reads the expected text from this design file on disk — never retyped — and requires a byte-for-byte line match in each target, plus, for the two anchored blocks, that each sits directly after its anchor line. The anchor matters on its own: the angle inserted after the `Pinned template` paragraph instead would separate it from the header that introduces it, leave a `diff`-mode angle trailing the two `design`/`plan` notes, and pass every other check here. It also asserts each file's length, using `check-sync.py`'s own `wc -l` convention so "89" means the same thing in both steps. Copy the script exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing. **The fence is unindented on purpose** — a `python3` heredoc indented under the list item is an `IndentationError`.

```sh
python3 - <<'PY'
import sys
from pathlib import Path
DESIGN = "docs/superpowers/specs/2026-07-29-gh-20-diff-terminology-design.md"
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
assert [len(b) for b in blocks] == [1, 1, 1, 2, 1, 1, 1, 1, 1, 1], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
GLOSS = ["CONTEXT.md"]
WANT = {PAIR[0]: 89, PAIR[1]: 89, GLOSS[0]: 67}
SPEC = [("line 28, diff row",            blocks[0], None,                    PAIR),
        ("line 29, design row",          blocks[1], None,                    PAIR),
        ("line 34, angles header",       blocks[2], None,                    PAIR),
        ("glossary-conformance angle",   blocks[3], "**Seam placement:**",   PAIR),
        ("terminology pass",             blocks[4], None,                    PAIR),
        ("rubric bullet 3",              blocks[5], None,                    PAIR),
        ("rubric bullet 7",              blocks[6], None,                    PAIR),
        ("resolution step 3",            blocks[7], None,                    PAIR),
        ("no-recursion clause",          blocks[8], None,                    PAIR),
        ("CONTEXT.md Angle entry",       blocks[9], "**Angle**:",            GLOSS)]
bad, text = [], {}
for path, want in WANT.items():
    L = Path(path).read_text(encoding="utf-8").split("\n")
    if L and L[-1] == "":
        L.pop()
    text[path] = L
    if len(L) != want:
        bad.append(("file length", path, "%d lines, want %d" % (len(L), want)))
for name, want, anchor, paths in SPEC:
    for path in paths:
        L = text[path]
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

   Expect exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — re-paste that block from *Exact change list* and re-run from step 1. The shape assertion (`[1, 1, 1, 2, 1, 1, 1, 1, 1, 1]`) fires if this document's plain-fenced blocks are ever added to, removed, reordered, or reflowed: that is deliberate, because the blocks are indexed positionally, and the expected shape was updated from the #20-only design's `[1, 1, 2, 1]` when #22's blocks were added, and again when the two Resolution-procedure repairs joined them. **Position matters, not just count:** the two new blocks sit between rubric bullet 7 and the `CONTEXT.md` **Angle** entry, so the glossary block moved from index 7 to index 9 and the `SPEC` table was renumbered with it. Every other fenced block in this document carries an info string (`text`, `sh`) and is therefore skipped by the `mode == ""` filter, so adding or editing a verification step never disturbs that index — **keep it that way: any new block that is not a change-list block must carry an info string.**
6. Both `plugin.json` versions read `2.6.0` and `1.8.0`.
7. **The three duplicated spans are byte-identical, not paraphrased.** *Why the never-flag clause is restated* depends on all three, and no mechanical check covers a duplication living twice inside one file. Each expects **4** — two passages × two mirror copies. The pathspec is required, because this design quotes all three in prose. The third span carries **no surrounding parenthesis or dash**: the pass parenthesizes it and the angle sets it off with an em dash, so a pattern including either delimiter returns 2 on a correct tree and proves nothing about the other passage.

   ```sh
   for s in "proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one." \
            "The same term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate." \
            "\`CONTEXT.md\` at the repo root, or the per-context files a root \`CONTEXT-MAP.md\` names"; do
     git grep -c -F "$s" -- plugins/ | awk -F: '{s+=$2} END {print s+0}'
   done
   ```

   Expect `4`, `4`, `4`. Today they are `2`, `0`, `2` — measured, not assumed.
8. **Behavioural check, after installation.** The running review loads the *installed* skill, not the branch's copy, so this step is meaningful only after `claude plugin marketplace update taylor-plugins` and a restart — during this change's own pipeline run the reviews still execute the pre-change text. Once installed:
   - **`diff` mode.** Run the review on this change's branch. The angle fires — this repo has a glossary, and the diff's added lines **of shipped text** are the mirror-pair edits and `CONTEXT.md`'s **Angle** entry, which between them use `angle`, `seed`, `glossary`, `simplification`, and `seam`. Every one of those is the glossary's own sense, so the correct outcome is **no finding**. A finding whose `file:line` falls under `docs/superpowers/` is evidence the scope clause is too weak to have shipped; a finding on the repaired rubric bullets' `seam` is evidence the second clause is.
   - **`design` mode.** Run the review on this document, which is a ready-made adversarial case for the drift clause rather than a friendly one: 104 occurrences of `boundary`, **28** of them in a Seam-sense phrase across 15 lines, and **none** in this document's own voice — 11 are greps searching for those exact strings, 17 are quotations of the rubric, of `0a8a158`, of #16's review, or of the records the census cites. The correct outcome is **no finding**, and a finding is diagnostic rather than merely disappointing: one on any of those 28 means the mention-versus-use sentence is too weak to have shipped; one on a stage-transition occurrence means *"only where it names the very concept its entry defines"* is. A finding that quotes **Seam**'s definition, a use in this document's own voice, and a location is a *correct* finding and means this document drifted — fix the document, not the clause.
   - In both modes, a report of "several identifiers overlap glossary terms" with no location is evidence the reportability rule is too weak to have shipped.

## PR

The PR body closes both issues:

```text
Closes #20
Closes #22
```

## Assumptions recorded

- **`CONTEXT.md` is the glossary filename in repos that have one, and `CONTEXT-MAP.md` names the per-context files in multi-context repos.** Taken from `docs/agents/domain.md`, byte-identical to the upstream file `setup-matt-pocock-skills` installs, and already relied on by #16's shipped pass. Verified: `CONTEXT-MAP.md` does not exist in this repo, which is single-context. Repos using a different glossary filename get the no-op path, which is the fallback and is correct rather than broken.
- **`_Avoid_:` is concept-scoped, not word-scoped.** Read from `docs/agents/domain.md`'s own sentence — *"When your output **names a domain concept** …"* — not inferred. The whole `_Avoid_: boundary` answer rests on it: if the rule were word-scoped, 27 legitimate shipped occurrences would be violations and the entry would have to be narrowed. A repo whose `_Avoid_:` convention *is* word-scoped gets over-reporting on that repo's common words, filtered by the discriminator and the reportability rule; the failure is seed cost, not a wrong answer.
- **A glossary entry's rejected names are recognizable without knowing the marker's spelling.** Both pieces of shipped text say "marks as one to avoid" rather than `_Avoid_:`. If a repo writes its rejections in a form a reader cannot recognize as rejections, the drift clause degrades to nothing and the angle's drift half with it, while both collision halves still work — a graceful partial failure, not a wrong answer.
- **A seed can tell a naming use from an ordinary-English one, and a mention from a use, given the term and the reference sense.** The first is load-bearing in both halves; the second only in the drift clause, which is why only it states the exclusion. Both are semantic, so they can fail either way. Under-detection is the status quo: drift missed, nothing spent. Over-detection costs seed-side reads and is then filtered twice — by the concept clause (the sense must actually differ from, or match, the entry's) and by the reportability rule (two quotable senses plus a location). The failure this can produce is seed cost, not the 86k-token one. See *Honest limit of the discriminator*.
- **The drift clause's cost is recurring where the angle's is not**, because the pass ships into two modes and runs on every dev-flow artifact. That asymmetry is priced in *What it costs per run* and is what forced the `_Avoid_: boundary` question to be answered rather than deferred. If a future change makes design/plan reviews rarer or cheaper, the pricing loosens; it never tightens.
- **The glossary stays small, and a multi-context `CONTEXT-MAP.md` is the same risk arriving by a second route.** 17 entries here, in one file, 6 rejected names. The design guards against neither a 500-entry glossary nor a `CONTEXT-MAP.md` naming many contexts — together the one place the fixed-N bound is not actually fixed, and a gap inherited by copying #16's glossary-location clause verbatim rather than re-specifying it. #16 recorded the same non-guard and its reasons hold: no multi-context repo and no large glossary is in evidence, and any threshold would be an invented number. The exposure differs by half — the collision half has grep as its fallback, so an unbounded glossary costs it precision, whereas for the angle and the drift clause the glossary *is* the bound. The cost is a longer search, not a wrong answer. A `CONTEXT-MAP.md` naming files that do not exist is not a separate case: it yields nothing to iterate and routes to the no-op by construction. If either appears, the answer is scoping by `CONTEXT-MAP.md` relevance — `docs/agents/domain.md`'s own "relevant to the topic" rule, which #16 also drops — which is a different change.
- **Design and plan records live under `docs/superpowers/`.** The path is dev-flow's own convention, already hardcoded in #16's shipped pass for the same reason. It bounds the angle's search and the collision half's grep; it never bounds the drift clause, which reads whatever artifact the review was handed regardless of path. A repo that keeps design records elsewhere gets them searched by the angle — a partial degradation into extra seed-side reads, not a wrong answer, and the same shape as the marker assumption above.
- **Line numbers 28, 29, 34, 40, 46, 54 and 58 in the mirror pair, and 30 in `CONTEXT.md`, are current as of `0a8a158`**, and lines 28, 29, 34, 46, 54 and 58 were verified identical between the two mirror copies before this design was written. The plan re-derives them by content match rather than trusting the numbers; the conformance script in Verification step 5 matches on text and anchors, never on line number.
</content>
</invoke>
