# Duplicate the two dev-flow variants rather than share a source file

`dev-flow` and `dev-flow-worktree` are the same pipeline differing on one axis — whether the feature branch is checked out in your current tree or in an isolated git worktree — and their skill files are near-identical copies. This is forced, not lazy: **each plugin installs alone into a version-keyed cache directory holding only its own tree**, and a user can install one without the other. There is therefore no runtime path from one plugin to a file in the other. The marketplace clone that does contain both is a harness-internal path tracking marketplace HEAD, not the pinned version-keyed cache the runtime loads, so referencing it would introduce silent version skew.

We control the resulting drift mechanically where the file structure allows and by hand where it does not. `scripts/check-sync.py` enforces the `adversarial-review/SKILL.md` pair as a **mirror pair** — line-for-line identical after substituting `dev-flow-worktree` → `dev-flow`, minus declared exceptions — and runs on every PR. The pipeline `SKILL.md` pair is a **hand-mirrored pair**: the two files differ in length (277 vs 271 lines), much of that divergence is deliberate namespacing, and the check's schema expresses only same-index one-line-for-one-line divergence, so enrolling them is structurally impossible rather than merely unwanted.

## Consequences

A one-sided edit to the hand-mirrored pair passes every check in CI. Changes touching it must carry their own verification — see the residue-grep and design-conformance rules in `CLAUDE.md`, both of which exist because this gap was hit in practice.

## Revisit when

The plugin system grows a contractual shared-asset mechanism. The fallback shape, if it ever matters, is one plugin exposing two entry skills — at the cost of coupling both variants to a single version stream, which is exactly the coupling the original split removed.
