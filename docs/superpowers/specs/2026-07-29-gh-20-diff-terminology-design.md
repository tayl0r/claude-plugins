---
dev-flow:
  slug: gh-20-diff-terminology
  stops: [post-design]
  docs: commit
---

# gh-20: `diff`-mode reviews have no terminology coverage

## Goal

Close issue #20 with one trigger-gated **sixth angle** on `adversarial-review`'s `diff`-mode quality seed, so a diff that uses a glossary term for something the glossary does not define — or reintroduces a synonym the glossary marks as one to avoid — is reported as a finding instead of shipping. The angle iterates the **glossary's** entries and searches the diff for each, never the reverse. It is findings-only and read-only: it never renames anything, never writes `CONTEXT.md`, and never proposes creating one. Nothing lands in the design rubric, the verbatim `/simplify` four-bullet block, the resolver tier, or `design`/`plan` mode.

## Scope check — one change, one mirrored pair

This is not two subsystems. It is one angle, added to one block, in one `check-sync.py`-declared mirror pair, plus the glossary entry that enumerates the block's contents and the two version bumps the install cache requires. Five files, one commit, no decomposition.

## The gap, restated precisely

Confirmed by reading both `diff`-mode seeds on `main` (`0a8a158`):

- The **correctness** seed is the pinned superpowers `code-reviewer.md`, used as designed. Its "What to Check" list covers plan alignment, code quality, architecture, testing and production readiness, with no naming, vocabulary or terminology item. The template is pinned and filled at four placeholders only, so `diff`-mode correctness cannot be extended without unpinning it.
- The **quality** seed's five angles — reuse, simplification, efficiency, altitude, seam placement — are all structural. None asks what anything is called.

So any coverage has to be a sixth quality angle. That is the issue's constraint and it survives inspection.

**What #16's pass leaves open.** #16 (shipped in `0a8a158`) added a terminology-collision pass to the `design`/`plan` **correctness** seed. It catches terms where they are coined, which is where all of its evidence sat. Two holes survive:

1. **Standalone `diff` reviews get nothing.** `adversarial-review(<PR#>, diff)` is a supported entry point in the Invocation contract, and a PR that never went through dev-flow has no design stage to have caught anything.
2. **Names invented at execution time are never checked.** A design says "a terminology pass"; the implementer writes `checkVocab()`. No design-stage reviewer can see that name.

**Honest narrowing.** The angle designed here closes hole 1 completely — every `diff` review of a repo with a glossary now runs a terminology check — and closes hole 2 **only where the invented name collides with a glossary term**. An execution-time name colliding with a sense that lives only in shipped prose, which is what #16's grep half catches for design docs, is still uncovered in `diff` mode. That narrowing is deliberate and is the entire reason the check is affordable; see *The decision*. The issue's framing implies hole 2 is closed outright, and it is not.

## Where the change lands

| Mode | Seed | Concretely |
|---|---|---|
| `diff` | **quality** | A sixth angle in the angles block, outside the verbatim `/simplify` four-bullet list, with the block header and the `diff` row's quality cell updated to name it |

Same slot and same shape as gh-7's seam-placement angle, which is the precedent the issue cites. Nothing lands in the design rubric — that ruling is gh-7's and gh-16's, unchanged, and applies here for the same reason: the rubric is the design/plan quality seed's lens **and** every resolver's judgment criteria in all three modes, making it the widest-broadcast text in the file, and this is a *noticing* obligation for one seed in one mode, not a statement of what "best long-term design" means for a decider.

Nothing lands in the four `/simplify` bullets, which are transcribed verbatim from a harness built-in with no readable file to point a subagent at. Editing them would silently fork a quotation.

## The decision — iterate the glossary, not the diff

The angle's three stages, in order:

1. **Read the glossary.** `CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names. No entries to iterate → the angle stops here and reports nothing.
2. **Grep, mechanically.** For each entry's term, and for each synonym the entry marks as one to avoid, grep the diff's **added lines of shipped text** for that term — case-insensitively, and in the joined spellings a multi-word term takes as an identifier — skipping design/plan records (`docs/superpowers/`). Those discuss the vocabulary rather than ship it, so every glossary term appears in them by construction — in *mention* rather than *use*, a distinction harder to draw than the naming discriminator this angle is built on. #16's pass excludes the same path for the same reason ("history, not shipped text"). Literal, cheap, and on shipped text most terms return zero hits in most diffs.
3. **Judge, only on hits.** A hit is a candidate only where the diff uses the term as a *name*, and then only if it names something the entry does not define, or reintroduces an avoided synonym for the concept it does.

### What the fixed-N argument buys, and what it does not

The issue says the glossary's entry count being "small, fixed, and independent of diff size … is what kills the false-positive problem." That is half right, and the half it misses is where the design work is.

Fixed N bounds **how many questions get asked**: 17 terms plus 6 avoided synonyms in this repo, 23 literal searches, the same number on a 40-line diff and a 4,000-line one. That is a real and decisive win over the diff-side direction, whose candidate set grows with the diff.

Fixed N does **not** bound **how many wrong answers come back**. Glossary terms are frequently ordinary English — this repo's glossary alone contains `pass`, `family`, `stop`, `artifact`, `angle`, `trigger`, `seam`, and the avoided synonym `boundary`. A Python diff has `pass` on every other function stub; a CI diff has `artifact` throughout; `boundary` appears 20+ times in this repo's own shipped prose meaning "stage transition". Step 2 will hit constantly, and on this repo's own diffs almost every hit is in prose *about* the vocabulary rather than prose that ships it. Measured on `0a8a158`, the last comparable change: **985 of its 996 added lines were dev-flow's own design and plan records**, carrying **285 of the 296 glossary-term hits** (`pass` 103, `seed` 60, `artifact` 48) and **all five** of its avoided-synonym hits. Its 11 added lines of shipped text carried 11 term hits and no avoided synonym at all. Two things then have to stop the remainder from reaching a resolver group, because gh-7's run measured one false-positive resolver group at **86,022 tokens**. The first is step 2's scope: shipped text only. The second is step 3.

### The naming discriminator

That something is step 3: **a hit counts only where the diff uses the term as a name** — an identifier, a field, a type, a user-facing or logged string, or prose that labels a concept. A term carrying its ordinary-English meaning inside a sentence names nothing and is not a candidate.

This is a narrower judgment than the one #20 correctly rejects for the diff-side direction. There, the seed must decide *"is `checkVocab` a domain concept?"* across dozens of unfamiliar identifiers with no reference to compare against. Here the term is fixed and supplied, the reference sense was read verbatim from the glossary one step earlier, and the question is only *"is this occurrence a name, and does it mean that?"* — a comparison, not an invention. Two live examples from this repo, both of which the discriminator handles correctly:

- The design rubric's *"Judge findings together, not in isolation"*. `judge` is an avoided synonym for **Resolver**. Here it is a verb describing an act, naming nothing. **Not a candidate.**
- The pipeline files' *"at each artifact boundary"*. `boundary` is an avoided synonym for **Seam**. Here it means a stage transition, which is not the concept **Seam** defines. **Not a candidate** under the second clause even if read as a naming use.

### The avoided-synonym half is a different failure, and needs saying so

The issue asks for `Avoid:` synonyms on the grounds that "a diff reintroducing an avoided synonym is the same failure." It is not quite the same failure, and collapsing them would leave the check unstatable.

- A **collision** is one word carrying two senses: the glossary's and the diff's.
- **Drift** is one concept carrying two names: the glossary's preferred term and a name it explicitly rejected.

They share a trigger, a search, and a reportability shape, which is why they belong in one angle rather than two. But their candidacy clauses are inverses — a collision requires the diff's sense to *differ* from the entry's, drift requires it to *match* — so the shipped text states both, in one sentence, rather than one and a hand-wave. `docs/agents/domain.md` already carries the repo-side rule ("Don't drift to synonyms the glossary explicitly avoids"); this makes it checkable at the one stage that can see an execution-time name.

The half is nearly free: the synonyms sit in the entry the seed just read, and the match is literal. And it has evidence. During #16's own design review, an earlier draft's `family` collision was reworded to *"the shared boundary"* — walking straight into **Seam**'s `_Avoid_: boundary` — in a document written by the author of the collision check. That is exactly the class of thing no structural angle looks for.

### The reportability rule

Report only what can be quoted: **the glossary's sense, the diff's sense, and the `file:line` where the diff's sense lives.** Same rule as #16, same reason — it is the second filter, after the naming discriminator, standing between a step-2 hit and an 86k-token resolver group. `"this name is confusing"` is not a finding, exactly as `"define your terms"` is not one in #16.

Findings only. A mismatch does not imply a rename, so it is reported either way; whether to rename is the resolvers' call. This mirrors #16's ruling, for #16's reason: a seed that finds one and privately judges the rename unwarranted is indistinguishable from the gap being closed.

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

**The shipped angle text names none of this.** It says "each synonym its entry marks as one to avoid", not `_Avoid_:`. That is deliberate: `adversarial-review` is a general-purpose skill that runs on other people's repos, and `_Avoid_:` is one convention — the one `docs/agents/domain.md` (byte-identical to the upstream `domain-modeling` file) happens to produce. Hardcoding the marker would make the half silently dead in any repo that writes "Not: " or "Deprecated: " instead. A seed reading a glossary can see which line rejects names without being told its exact spelling.

**`CONTEXT-MAP.md` — verified, not assumed.** It does **not** exist in this repo; `find` and `git grep` return it only inside prose. The mechanism is real, not an aspiration: `docs/agents/domain.md` documents it as the multi-context layout ("`CONTEXT-MAP.md` at the repo root if it exists — it points at one `CONTEXT.md` per context"), and #16's shipped pass already names it in exactly this phrasing. This repo is single-context, so in practice the angle reads root `CONTEXT.md`.

The glossary-location clause is therefore **copied verbatim from the terminology-collision pass** — `` (`CONTEXT.md` at the repo root, or the per-context files a root `CONTEXT-MAP.md` names) `` — rather than paraphrased. Two checks now depend on the same fact about where a glossary lives; identical strings make them one greppable fact, and a future change to the glossary convention edits two identical spans instead of hunting a paraphrase.

## The open question, answered

> *"the check has no fallback … the angle is a silent no-op in most repos … Worth confirming that a no-op angle still earns its ~150 tokens in the widest-broadcast diff prompt."*

**Answer: it earns its place. Ship it.** Two parts of the question's premise need correcting first, and one part of it is right and worth naming.

**"Widest-broadcast" is the wrong label for this slot.** `CONTEXT.md` reserves that phrase for the **design rubric**, which ships into every resolver in all three modes *and* the design/plan quality seed. The angles block is carried by exactly one prompt — the `diff`-mode quality seed — plus the orchestrator's single whole-file load. That is *narrower* broadcast than #16's 235-word addition, which the correctness seed carries in two modes. The measured figure: this change adds **242 words** (~340 tokens) to a 2,472-word file, ~9.8% of the file, and against gh-7's real review invocation of 484,005 tokens the growth is roughly **0.070%** — versus 86,022 tokens for one false-positive resolver group, ~253×. The ratio gh-7 established is not close.

**"Silent no-op in most repos" is the established shape of every gated check in this file, not a defect unique to this one.** Seam placement (200 words) is a no-op on every diff adding no bridge construct, which is most diffs. Input-contract completeness (114 words) is a no-op on every artifact accepting no new outside input. Terminology collision (217 words) is a no-op on every artifact coining no term. A frequency-of-firing bar would retroactively disqualify all three, including both of gh-7's families.

**The part that is right, and does need stating:** this trigger is a property of the **repo**, not of the artifact. The other three fire or not per-artifact; this one is either always-on or never-on for a given repo. In a repo with no glossary it is permanently dead weight rather than occasionally dead. That is a genuinely different failure shape and the issue is correct to flag it.

It still wins, on four counts:

1. **The cost is ~340 tokens, paid twice per `diff` review.** There is no competing use for them; skill context here is not a rationed budget, and the comparison that governs is against the 86k-token FP group, not against zero.
2. **The trigger is cheap to fail.** One file read. A seed in a glossary-less repo reads one sentence, finds nothing to iterate, and stops — it does not grep, judge, or report.
3. **The repo that ships this has a glossary.** Every dev-flow `diff` review of these plugins fires the trigger, on diffs to the very prose the glossary defines. The "most repos" denominator excludes the case where the check's own maintenance happens.
4. **The alternative that would make the no-op cost literally zero is worse.** See *Conditional prompt assembly*, below.

**The design must state the no-op rather than let it be discovered**, which the issue asks for and which the shipped text does, in its last clause: *"Where the glossary yields no entries to iterate this angle reports nothing: proceed silently."* The condition is closed by construction rather than enumerated, as #16's is: a missing file, an empty one, a file that is not a glossary, and a `CONTEXT-MAP.md` path that does not resolve all yield no entries and all route here. That sentence also carries the never-flag-the-glossary rule; see *Why the never-flag clause is restated*.

**What would change the answer.** If a future change makes the `diff` quality seed carry the design rubric as well, or if the angles list grows past roughly eight with several repo-level triggers among them, the right response is to restructure — gate the repo-level angles once as a group — not to delete this one. That threshold is stated so a future reader has a rule rather than a re-litigation.

## Why the never-flag clause is restated rather than shared

#16's pass ends *"the glossary's own state is never a finding: never flag it, never propose creating one."* This angle restates that rule. The rubric says to prefer the shared boundary over a per-instance fix, so the restatement needs a reason.

There is no shared boundary available that costs less than the restatement. The two checks live in different table rows, different seeds, and different modes; the `diff` quality seed prompt never contains the terminology-collision pass's text. Without the clause, a `diff`-mode seed in a glossary-less repo has every incentive to report the absent glossary as the finding — which is the pipeline's worst outcome per token, since the "finding" is unfixable by a review that is forbidden to write repo state. Inventing a shared "rules common to glossary-reading checks" section to hold one sentence would cost more prose than it saves and would be read by seeds that need only one of the two checks.

**The instance count is not what decides this, and this design should not lean on it.** After this ships, two checks carry the sentence, and the rubric's *"widen the lens only against concrete demand (planned siblings, 2+ instances)"* treats two as concrete demand rather than speculation — so the count is met, not pending. What the same bullet asks next is where the shared seam is, since *"zooming out finds the right boundary, it doesn't add layers"*, and here there is none to find. Each seed prompt is assembled from the sections its mode names and must be self-contained by the time it reaches a subagent; a "rules common to glossary-reading checks" section, in a file whose sections are cherry-picked into prompts, is not a seam but an indirection the prompt-builder has to remember to resolve for two of the three modes — the *"each caller must remember a flag, ordering, or manual step"* shape the rubric ranks below a correct-by-default one. Restating in place is the correct-by-default option: the check that reads a glossary carries the rule that governs glossary reading, with no assembly step to forget.

**What changes the answer is a seam appearing, not a count rising.** If prompt assembly ever gains a block both seeds include — the machinery *Conditional prompt assembly* rejects for the trigger — the sentence moves there. Until then the duplication is managed by making it byte-identical rather than paraphrased: the clause is copied verbatim from #16's pass, for the same reason the glossary-location clause is, so one `git grep -F` finds every instance as a single fact and a future change edits identical spans instead of hunting a paraphrase. A verification step asserts the count, because this duplication lives twice inside one file and `check-sync.py` only ever proves the two mirror copies agree with *each other*.

## Applying #16's terminology-collision pass to this document

The check #16 shipped, run against this design — including on the term this design coins.

- **`glossary conformance`** (coined here). `conformance` already ships in this repo's prose twice: `CONTEXT.md`'s **Provenance** entry ("Evidence of fan-out and tier conformance") and `CLAUDE.md`/ADR-0001's "design-conformance". Both mean *"X matches the standard it is supposed to match"*, which is exactly the sense here. Same sense; **no finding**.
- **`collision`** — used above for *"one word carrying two senses"*, and **not coined here**: `adversarial-review/SKILL.md:46` already ships that sense verbatim (*"**Against itself:** one word carrying two senses, or two words carrying one"*), so this document adopts the shipped word for the shipped concept. The pipeline pair's *"accidental branch collisions"* and *"Intake collision check"* (`plugins/dev-flow/skills/dev-flow/SKILL.md:68` and `:81`, mirrored at `plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md:66` and `:79`) are the ordinary computing sense — one identifier, two claimants — applied to branch names rather than words: the same relationship `drift` has across its three uses below. Same sense, different domain; **no finding**. Renaming would be the actual error, leaving one concept with two names across `SKILL.md:46` and this document — the drift half of the very check this design ships.
- **`drift`** — used here for the diff diverging from the glossary. The repo uses it for `check-sync.py`'s "mechanical drift check", `CLAUDE.md`'s hand-mirrored divergence, and the plan seed's "drift from the design doc". All mean *two things that should agree diverging*. Same sense; **no finding**.
- **`naming use`** (coined here) — no prior use anywhere in the repo. **No finding.**
- **`terminology collision`** — **fired, and the design changed because of it.** `CONTEXT.md` does not define it, but `adversarial-review/SKILL.md:46` ships it as the name of a specific `design`/`plan` correctness pass. Naming this angle "terminology collision" too would put one name on two checks with different mechanisms (artifact-side vs. glossary-side) in the same file — precisely the failure #16 exists to catch, committed in the file #16 edits. That is why the angle is called **glossary conformance**, and why this document says "terminology" only when referring to the topic or to #16's pass.
- **`angle`**, **`trigger`**, **`reportability rule`**, **`seed`**, **`resolver`**, **`pass`** — each used throughout in `CONTEXT.md`'s sense, checked by holding each fixed across the whole document. In particular `pass` appears here only for #16's named check, never in the ordinary-English "a run over a document" sense that #16's own review had to correct.

**Against itself:** no word carries two senses; `collision` and `drift` are explicitly separated in *The avoided-synonym half* precisely so they cannot.

## No tier name appears in the new text

gh-7 recorded a **standing obligation**: every future tier or protocol change must keep each added check coherent, "which is why neither pass restates a tier name", and #16 repeated it ("the pass names no tier"). Concretely, the Model section is the single place that says seeds run on `sonnet` and resolvers on `opus`; the `fable` → `opus` swap (#14) had to sweep every restatement of that fact, and each one is a place the sweep can miss.

The angle text contains no `sonnet`, no `opus`, and no "seed model". It says "the fix is the resolvers' call" — a **role** name, identical to the phrasing both existing passes use, and unaffected by any tier change. The obligation is honoured.

## Rejected alternatives

**A diff-side trigger restricted to exported/public names.** The strongest alternative, and the one #20's "Sketch" section is arguing against. Rejected on four counts, the third of which is decisive:

1. *The bound is not actually small.* One new module can export 20+ names and a feature-sized diff many more, against a fixed 23 literal searches here. The count also grows with diff size, which is the property the inversion exists to remove.
2. *"Exported/public" is not language-uniform.* Python has no keyword (a leading-underscore convention), Go uses capitalization, Rust `pub`, TypeScript `export`. A `sonnet` seed applying "public" across a polyglot diff is applying four different rules it has to infer.
3. **The repo this ships from is markdown.** `SKILL.md` prose has no notion of an export, so the trigger would not fire at all on the diffs that motivated this issue — the ones that edit `adversarial-review`'s own vocabulary. An alternative that is inert on the primary case loses to one that is not.
4. *The false-positive economics are the ones #20 already priced.* Each exported name needs a repo-wide grep to establish a colliding sense, and `config`, `client`, `handler`, `result` always hit. That is the 86k-token path.

It does buy one thing the chosen approach does not: an execution-time name colliding with a **non-glossary** shipped-prose sense. That is hole 2's residue, named in *The gap, restated*. It is not worth 86k tokens a group.

**Extend the existing seam-placement angle instead of adding a sixth.** Rejected. The two share nothing: seam placement's trigger is a structural property of a construct the diff adds, and it "proposes removals, never a restructuring" — a terminology finding proposes neither a removal nor a relocation. Merging them produces one paragraph with two unrelated triggers, which is exactly the degradation #16 refused when it declined to bolt a diff trigger onto its own pass. The issue's constraint says sixth angle for this reason, and inspection agrees.

**A third `diff`-mode seed, or a separate "vocabulary" seed.** Rejected, on #16's grounds unchanged: it raises `diff` seed cost by 50% for one question and breaks the uniform two-seed shape the whole Seed passes section and the provenance line (`seeds: N× <tier>`) are written around.

**Extend the `diff` correctness seed.** Not available. The pinned `code-reviewer.md` is used "as designed", with only four placeholders filled. Adding a terminology item means either unpinning the template — losing the property that makes it trustworthy and inheriting maintenance of an upstream file — or smuggling instructions through `[DESCRIPTION]`, which is not what that placeholder is. The issue states this and it holds.

**Conditional prompt assembly — omit the angle when no glossary exists.** Rejected, though it is the only option that drives the no-op cost to literally zero. It moves a trigger the seed evaluates in one read into the orchestrator's prompt-building step, where nothing else is conditional; it makes the header's "all six apply" false in the omitting case, so the header has to say "five or six"; it makes the angle count vary between two runs of the same skill, which the `CONTEXT.md` **Angle** entry and any future provenance-style check would then have to accommodate; and it saves nothing on the orchestrator's whole-file load, which is paid either way. It trades a fixed ~340 tokens for a variable-shape prompt. The rubric's "a fix must be worth its complexity" settles it.

**Also grep the repo for non-glossary senses, as #16's pass does.** Rejected. That is the exact cost #20 prices at ~86k tokens per false-positive group, and it re-imports the unbounded candidate set the inversion was designed to eliminate. The glossary is the whole bound; that is the trade, and the residue is named rather than hidden.

**Gate the review on a glossary existing.** Rejected, on #16's grounds unchanged: a shipped general-purpose skill must not assume one documentation convention, and turning a missing file into a halt is the pipeline's most expensive outcome.

## Out of scope

**`CONTEXT.md`'s `_Avoid_: boundary` entry.** Under **Seam**, that entry is arguably over-broad for a repo whose shipped prose uses "boundary" 20+ times legitimately ("artifact boundary", "stage boundary"). The naming discriminator handles it — those are stage transitions, not Feathers seams — but the residual imprecision is real (see *Honest limit*, below). Narrowing or removing the entry is a glossary change with its own argument and its own blast radius; this angle reads whatever the glossary says, and changing the glossary to suit the reader is the wrong direction. Not touched here.

**`docs/adr/`.** Same ruling as #16: ADRs record decisions, not vocabulary. The angle reads the glossary only.

**A `CONTEXT.md` entry for the check itself.** None is added beyond the **Angle** entry's enumeration, which must change because it lists its instances. `Pass`, `Trigger`, and `Reportability rule` already define the shape this is an instance of.

**`design`/`plan` mode.** #16 covers those, artifact-side. Adding a glossary-side check there too would ask the same question twice per artifact; the artifact-side direction is strictly better in prose, which is what #16 established. **One residue is named rather than hidden.** #16's pass fires only on words the artifact *introduces or adopts as the name of a concept*, so it does not catch an artifact drifting to an avoided synonym in passing — which is exactly what the `family` → *"the shared boundary"* rewording during #16's own design review was. Step 2's scope clause puts that case outside this angle too, deliberately: a design doc's vocabulary is the design stage's business, and closing it belongs in a drift clause on #16's pass, not in a `diff`-mode angle asked to separate mention from use across ~1,000 lines of prose about the glossary. Filed as https://github.com/tayl0r/claude-plugins/issues/22.

## Honest limit of the discriminator

The naming discriminator is a semantic judgment and can be applied too loosely. The known worst case in this repo: the design rubric's *"put the fix at the shared boundary so current and future members inherit it"* and *"zooming out finds the right boundary"*. Both use an avoided synonym for **Seam**, and both arguably *do* refer to a place where behaviour can be altered without editing in that place. A strict reader calls them ordinary-English noun phrases inside sentences, naming nothing, and reports neither; a loose reader reports both.

Two things bound the damage, and one thing that looks like a bound is not one. **The scope clause is the real bound.** Those two lines live in the design rubric, and the diffs that re-add phrasing like them are dev-flow's own design and plan records, which the angle no longer searches. Measured on `0a8a158`: 985 of 996 added lines were under `docs/superpowers/`, all five of that change's `boundary` additions were among them — one of them literally *"the fix belongs at the shared boundary"*, this section's own worst case, added by the last change to ship — and its 11 added lines of shipped text contained no avoided synonym. Added-lines-only bounds what is left: the rubric's own two lines are unchanged since gh-7 and produce nothing unless a diff re-adds them in shipped text.

**What is not a bound is the reportability rule**, and an earlier draft of this design claimed it was. It screens a reader who cannot say what the diff's sense *is*; it does not screen this case, where the sense is articulable — the paragraph above articulates it. A reader who calls *"the shared boundary"* a naming use can quote **Seam**'s definition, quote the diff's use, give a `file:line`, and satisfy the rule in full. So the residue is priced rather than argued away: a defensible drift finding on shipped text can reach a resolver and cost one group. That is the trade gh-7 already accepted for seam placement — *"budget one resolver group on that fraction of PRs"* — not a claim the rate is zero. The scope clause is what keeps the fraction small, and the comparison in *Context cost* is against a rate this design has shown it reduces by 96% on the repo it ships from, not against an event it merely asserts it avoids.

Success criterion for a future run, stated so it can be checked: a reported finding must quote the glossary entry, the diff's use, and a `file:line`. A run that reports "several identifiers overlap glossary terms" without those three is evidence the reportability rule is too weak to have shipped.

## Context cost

`adversarial-review/SKILL.md` is 2,472 words today. The addition is **241 words** in the angle, plus a net 2 in the `diff` row's quality cell and a net −1 in the angles-block header — **242 words**, about **9.8%** of the file, ~340 tokens. It is carried by the orchestrator's one whole-file load and by the `diff`-mode quality seed prompt; `design` and `plan` reviews pay only the former.

At 241 words the angle is now the longest single passage in the file, ahead of terminology collision at 217 and seam placement at 200 — about 11% longer than the previous longest. It is not a new order of magnitude, and the words it added over the earlier draft are the scope clause and the case-insensitivity clause, which are the two things *Honest limit of the discriminator* identifies as the real bound on false positives.

Measured against gh-7's real review invocation of 484,005 tokens, the growth is roughly **0.070%**. One false-positive resolver group measured 86,022 tokens, ~253× the entire addition. Every word spent on the trigger, the naming discriminator, and the reportability rule is therefore lopsidedly worth it, which is why all three are stated in full.

Per-clause marginal value was run over the angle's seven clauses and nothing was cut. The two weakest survive for stated reasons: *"never the diff's names"* is the whole inversion in three words and prevents a seed from helpfully expanding the iteration; *"The same term carrying its ordinary-English meaning inside a sentence names nothing"* is the single clause that keeps `pass`, `stop` and `artifact` from flooding step 3, and it is the difference between this angle and the one #20 rejects.

## Exact change list

Five files. Every wording below is literal.

### 1 & 2. `plugins/dev-flow/skills/adversarial-review/SKILL.md` and `plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md`

A declared `check-sync.py` mirror pair. **Every edit below lands byte-identically in both files.** None of the new or edited text contains a `dev-flow` or `dev-flow-worktree` token, so the two copies compare equal in every touched region before canonicalization does anything.

Three edits: two in-place line replacements and one two-line insertion. Both replacements are above the insertion point and in place, so neither shifts it. Line numbers are the current (pre-change) file, which is **87 lines**.

#### Line 28 — Seed passes table, the `diff` row

The quality cell names the angles the seed runs; a sixth is added, so the cell must name it or a prompt-builder resolving the cell ships five. Only the quality cell changes; the correctness cell is byte-identical to today. Replace the whole line with:

```
| **diff** | `/simplify`'s four angles plus this skill's seam-placement and glossary-conformance angles, inlined (below), findings-only, run against `BASE..HEAD`. | The superpowers `code-reviewer.md` template, used as designed (already read-only/findings-only) — see "Pinned template," below. |
```

**Lines 29 and 30 (the `design` and `plan` rows) are not edited.**

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

#### Resulting file shape

Both copies go from **87 to 89 lines**.

| Line | Content |
|---|---|
| 26–27 | table header, unchanged |
| **28** | `diff` row — **replaced** |
| 29–30 | `design` and `plan` rows, unchanged |
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
| 48 | `**Terminology collision — …` (was 46) |

### 3. `CONTEXT.md` — the glossary entry this change makes true

The **Angle** entry enumerates its instances, unlike **Pass**, so it goes stale the moment a sixth ships. `docs/agents/domain.md` has every skill read the glossary before exploring, so a stale enumeration sends an agent looking for a five-item list that no longer exists.

**The glossary changes with the thing it defines** — gh-7's ruling, which put its own `Angle` entry in the commit that shipped seam placement rather than in a follow-up. Same here.

Replace **line 30** (the definition line under `**Angle**:`) with:

```
One lens in the diff-mode quality seed's list: reuse, simplification, efficiency, altitude, seam placement, glossary conformance.
```

`CONTEXT.md` stays at **67 lines** — a one-line replacement, not an append. It ships into no plugin and `check-sync.py` never reads it.

No new entry is added. **Pass**, **Trigger** and **Reportability rule** already define the shape this angle is an instance of, and adding an entry per check is the glossary growing a row per line of `SKILL.md`.

### 4 & 5. Version bumps

The install cache is version-keyed (`~/.claude/plugins/cache/taylor-plugins/<plugin>/<version>/`), so a skill edit at an unchanged version is never picked up on re-sync.

| File | From | To |
|---|---|---|
| `plugins/dev-flow/.claude-plugin/plugin.json` | `2.5.0` | **`2.6.0`** |
| `plugins/dev-flow-worktree/.claude-plugin/plugin.json` | `1.7.0` | **`1.8.0`** |

Minor in both: the invocation signature, the contract, the provenance format, the mode set, and the model policy are all unchanged. Same bump shape as gh-7 (`2.3.0`→`2.4.0`, `1.5.0`→`1.6.0`) and gh-16 (`2.4.0`→`2.5.0`, `1.6.0`→`1.7.0`).

Neither `description` changes, so `.claude-plugin/marketplace.json` is not touched.

## Sync constraint — how `check-sync.py` still passes

**Check B (mirror pair `adversarial-review`)** requires the two files to be line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, except the declared exception at line 12.

1. **All three edits land in both files.** A one-sided edit produces an undeclared-divergence failure naming the line.
2. **The insertion is symmetric, so line counts stay equal.** Both files go 87 → 89. An asymmetric insertion is a `LINE_COUNT_FIX` failure and could not be declared as an exception even deliberately — the schema declares only same-index, one-line-for-one-line divergences.
3. **No new variant token is introduced.** Verified: the added and edited text contains no `dev-flow` or `dev-flow-worktree` occurrence.
4. **The declared exception still fires and does not go stale.** It covers line 12, above every edit, which does not shift.

**Check A (manifest descriptions)** compares `name`, `source`, and `description` between each `plugin.json` and its marketplace entry, and does not read `version`. This change edits only `version`, so `marketplace.json` is not touched and Check A is unaffected.

**No hand-mirrored file is edited.** Both pipeline `SKILL.md` copies and both `README.md`s are untouched (see *Blast radius*), so the pair with no mechanical check behind it stays out of this change entirely.

## Blast radius

A repo-wide search of tracked files outside `docs/superpowers/` for `angle`, `angles`, `simplify`, and `quality seed` returns hits **only** in the two `adversarial-review/SKILL.md` copies and `CONTEXT.md`:

```sh
git grep -n -w -i -e angle -e angles -e simplify -e 'quality seed' -- . ':!docs/superpowers/'
```

`-w` is load-bearing here, not tidiness: without it `angle` matches `mangled` in `CLAUDE.md:9` — *"text mangled identically in both sides passes it"* — and the **only** claim is false. That is precisely the substring-inside-an-unrelated-word false positive the naming discriminator exists to survive (`pass` in a Python stub, `artifact` in a CI diff), turning up in this document's own scope check; `angle` is the first bare common word this formula has been pointed at, which is why gh-7's and gh-16's substring searches were sound and this one is not. `-e angles` is redundant today — every plural line also carries `/simplify` or `quality seed` — and is stated anyway, because a future *"the six angles"* line would carry neither, and a blast-radius search that misses one is a silent scope error. **Do not carry `-w` forward as a house rule:** it is chosen per pattern, and it would break gh-7's `seed pass`, which matches only as a substring of *"Seed passes"*. Specifically confirmed:

- **`plugins/dev-flow/skills/dev-flow/SKILL.md`** and **`plugins/dev-flow-worktree/skills/dev-flow-worktree/SKILL.md`** — **zero hits**. They invoke the review by mode and delegate seed content entirely; neither enumerates an angle. The hand-mirrored pair stays out of this change.
- **Both `README.md` files** — **zero hits** for `angle`, `simplify`, or `quality seed`.
- **The `Working directory` section of the mirror pair** — **not edited, and this is load-bearing.** This angle is the fourth read-only reviewer needing the repo root, after both `diff`-mode seeds and #16's pass. The sentence #16 landed at the shared boundary — *"Read-only reviewers receive that root as well as absolute paths for every file the review hands them"* — already covers it. That is the shared-boundary fix paying off exactly as the rubric predicts: the per-instance alternative would have needed a restatement here.
- **`.claude-plugin/marketplace.json`** — no `description` change; Check A does not read `version`.
- **`CLAUDE.md`** — untouched. The mirrored-pair verification rule gh-7 landed already covers this change as written (residue grep plus a per-change conformance script), and this change is exactly the case it describes.
- **`docs/agents/domain.md`** — untouched. Its "Don't drift to synonyms the glossary explicitly avoids" rule is already true; this change makes it checkable at the `diff` stage, it does not restate it.
- **`scripts/check-sync.py`**, **`.github/workflows/`**, **`docs/adr/`** — untouched.

## Verification

1. `python3 scripts/check-sync.py` — passes. Expect `mirror pair "adversarial-review" ... OK (89 lines, 1 declared exception)`.
2. `claude plugin validate .` — passes; the 8 missing-author warnings are expected.
3. **Residue grep (always, per `CLAUDE.md`).** All three return **no hits**:

   ```sh
   git grep -n -F -e 'seam-placement angle, inlined' \
                  -e "then a fifth of this skill" \
                  -e 'altitude, seam placement.' -- plugins/ CONTEXT.md
   ```

   All three are text this change deletes: the first two are the in-place replacements in the mirror pair (currently 2 hits each, one per copy), the third is `CONTEXT.md`'s stale five-item enumeration (currently 1 hit). A surviving hit on either of the first two means one side of the mirror pair was missed — the failure `check-sync.py` catches only if the *other* side changed. The pathspec is required: this design quotes all three strings in prose, and `docs/superpowers/` must not be searched.
4. **Design conformance — all four blocks landed verbatim, in the right place.** This is the step steps 1–3 structurally cannot provide. Step 3's residue grep is tied to the two in-place replacements and says nothing about the insertion, and `check-sync.py` compares the two mirror copies only to *each other*, so a word mangled identically in both passes it at the correct 89 lines — and it never reads `CONTEXT.md` at all. This check reads the expected text from this design file on disk — never retyped — and requires a byte-for-byte line match in each target, plus, for the two anchored blocks, that each sits directly after its anchor line. The anchor matters on its own: the angle inserted after the `Pinned template` paragraph instead would separate it from the header that introduces it, leave a `diff`-mode angle trailing the two `design`/`plan` notes, and pass every other check here. It also asserts each file's length, using `check-sync.py`'s own `wc -l` convention so "89" means the same thing in both steps. Copy the script exactly; it is deliberately pure ASCII, so a mistyped copy fails loudly instead of passing. **The fence is unindented on purpose** — a `python3` heredoc indented under the list item is an `IndentationError`.

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
assert [len(b) for b in blocks] == [1, 1, 2, 1], "design code-block shape changed; stop and re-read the design"
PAIR = ["plugins/dev-flow/skills/adversarial-review/SKILL.md",
        "plugins/dev-flow-worktree/skills/adversarial-review/SKILL.md"]
GLOSS = ["CONTEXT.md"]
WANT = {PAIR[0]: 89, PAIR[1]: 89, GLOSS[0]: 67}
SPEC = [("line 28, diff row",            blocks[0], None,                    PAIR),
        ("line 34, angles header",       blocks[1], None,                    PAIR),
        ("glossary-conformance angle",   blocks[2], "**Seam placement:**",   PAIR),
        ("CONTEXT.md Angle entry",       blocks[3], "**Angle**:",            GLOSS)]
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

   Expect exactly `design-conformance: OK` and `exit=0`. A `MISMATCH` line names the block and the file whose text or position differs — re-paste that block from *Exact change list* and re-run from step 1. The shape assertion (`[1, 1, 2, 1]`) fires if this document's plain-fenced blocks are ever added to, removed, or reflowed: that is deliberate, because the blocks are indexed positionally. Every other fenced block in this document carries an info string (`text`, `sh`) and is therefore skipped by the `mode == ""` filter, so adding or editing a verification step never disturbs that index — keep it that way.
5. Both `plugin.json` versions read `2.6.0` and `1.8.0`.
6. **Behavioural check.** Run the pipeline's own `diff`-stage review on this change's branch. The angle fires — this repo has a glossary, and the diff's added lines **of shipped text** are the three mirror-pair edits and `CONTEXT.md`'s **Angle** entry, which between them use `angle`, `seed`, `glossary`, and `simplification` — and the bar for what it may report is the reportability rule: any finding must quote the glossary entry, the diff's use, and a `file:line`. A run that reports the absence of something, or "several identifiers overlap glossary terms" with no location, is evidence the last clause or the reportability rule is too weak to have shipped. A finding whose `file:line` falls under `docs/superpowers/` is evidence the scope clause is too weak to have shipped.
7. **The restated clause is byte-identical, not paraphrased.** *Why the never-flag clause is restated* depends on it, and no mechanical check covers a duplication living twice inside one file. Expect exactly `4` — two passages × two mirror copies. Currently `2`; the pathspec is required, because this design quotes the span in prose.

   ```sh
   git grep -c -F "proceed silently — the glossary's own state is never a finding: never flag it, never propose creating one." -- plugins/ | awk -F: '{s+=$2} END {print s+0}'
   ```

## Assumptions recorded

- **`CONTEXT.md` is the glossary filename in repos that have one, and `CONTEXT-MAP.md` names the per-context files in multi-context repos.** Taken from `docs/agents/domain.md`, byte-identical to the upstream file `setup-matt-pocock-skills` installs, and already relied on by #16's shipped pass. Verified: `CONTEXT-MAP.md` does not exist in this repo, which is single-context. Repos using a different glossary filename get the no-op path, which is the fallback and is correct rather than broken.
- **A glossary entry's rejected names are recognizable without knowing the marker's spelling.** The angle says "each synonym its entry marks as one to avoid" rather than `_Avoid_:`. If a repo writes its rejections in a form a reader cannot recognize as rejections, the drift half degrades to nothing while the collision half still works — a graceful partial failure, not a wrong answer.
- **A seed can tell a naming use from an ordinary-English one, given the term and the reference sense.** This is the angle's load-bearing assumption and it is semantic, so it can fail either way. Under-detection is the status quo: collisions missed, nothing spent. Over-detection costs seed-side reads and is then filtered twice — by the second clause (the sense must actually differ from, or match, the entry's) and by the reportability rule (two quotable senses plus a `file:line`). The failure this can produce is seed cost, not the 86k-token one. See *Honest limit of the discriminator* for the concrete worst case in this repo.
- **The glossary stays small, and a multi-context `CONTEXT-MAP.md` is the same risk arriving by a second route.** 17 entries here, in one file. The design guards against neither a 500-entry glossary nor a `CONTEXT-MAP.md` naming many contexts — together the one place this angle's fixed-N bound is not actually fixed, and a gap inherited by copying #16's glossary-location clause verbatim rather than re-specifying it. #16 recorded the same non-guard and its reasons hold here: no multi-context repo and no large glossary is in evidence, and any threshold would be an invented number. The reason to restate rather than inherit silently is that the exposure differs — #16 has grep as its fallback, so an unbounded glossary costs it precision, whereas here the glossary *is* the bound. The cost is a longer step-2 grep, not a wrong answer. A `CONTEXT-MAP.md` naming files that do not exist is not a separate case: it yields no entries and routes to the no-op by the closing clause's construction. If either appears, the answer is scoping by `CONTEXT-MAP.md` relevance — `docs/agents/domain.md`'s own "relevant to the topic" rule, which #16 also drops — which is a different change.
- **Design and plan records live under `docs/superpowers/`.** The path is dev-flow's own convention, already hardcoded in #16's shipped pass for the same reason. A repo that keeps design records elsewhere gets them searched — a partial degradation into extra seed-side reads, not a wrong answer, and the same shape as the `_Avoid_:`-marker assumption above.
- **Line numbers 28, 34 and 40 in the mirror pair, and 30 in `CONTEXT.md`, are current as of `0a8a158`.** The plan re-derives them by content match rather than trusting the numbers; the conformance script in Verification step 4 matches on text and anchors, never on line number.
