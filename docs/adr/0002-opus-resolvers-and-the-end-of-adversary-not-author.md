# Resolvers run on opus; `adversary ≠ author` is abandoned

`adversarial-review`'s group-resolution tier previously ran on `fable`, justified as running the adversary on a model **family** different from whatever authored the artifact, with an `opus` fallback when the session was already Fable-family. As of `dev-flow` 2.3.0 resolvers run on `opus` unconditionally and the `fable` alias is gone from the protocol, including from the provenance `<tier>` enum. Since the session model — and therefore the author — is normally Opus, author and adversary are now the same family by design.

The property was given up knowingly, on the judgment that Opus 5 closed enough of the capability gap that Fable's premium no longer earned its cost. What survives is *contextual* independence: a fresh context window with no memory of authoring, an explicitly adversarial prompt, and `sonnet` seeds that remain cross-family from an Opus author and determine what gets noticed. What is lost is *prior* independence — uncorrelated training blind spots — concentrated in the resolvers' subtle judgment calls, and most exposed in Stage 4's diff review, where implementers and resolvers are now the same family.

A related correction rode along: the provenance check never verified `adversary ≠ author` in the first place, because it has no knowledge of the author's model. It verifies that the review genuinely fanned out into separate reviewer subagents on the declared tiers instead of collapsing into a single inline pass. Prose across four files was rewritten to claim only that.

## Considered options

- **Invert the fallback** (default `opus`, fall back to `fable` when the session is Opus-family) — rejected: the fallback would fire on most runs, so the premium is still paid, and it leaves the resolver tier a function of ambient session state, turning a fixed provenance comparison into a stateful one.
- **Move the diversity guarantee onto the seeds** — rejected: making `sonnet` seeds a *guarantee* rather than an observation reintroduces the same ambient-state dependency, and mislocates the property on a findings-only tier that makes no judgment calls.
- **Drop the provenance line entirely**, since it cannot prove diversity — rejected: it is still the only mechanical evidence that "Review integrity (never inline)" was honoured. The description was wrong, not the check.
- **Record the author's model family in front-matter and enforce against it** — rejected: on a default Opus session an enforcing check fails every run, and its only escapes are a premium fallback or a capability cut. Diff mode has no front-matter to stamp, and standalone invocations have no author to record.
