---
name: address-pr-feedback
description: This skill should be used when the user asks to "address PR comments", "fix PR feedback", "resolve review comments", "handle CodeRabbit comments", "respond to PR reviews", or wants to check a PR for new comments and fix/respond to them. Also trigger when user says "check PR for new comments" or "address feedback on PR".
---

# Address PR Feedback

Fetch all unresolved review comments on a GitHub PR, evaluate each against the design rubric below, fix the ones that are a clearly better design, and post a response to every comment explaining what was done, what's pending your approval, or why it was skipped.

## Process

### Step 0: Pre-flight checks

Determine the PR number from the user's message or the current git branch. If unclear, ask.

```bash
# Detect owner/repo
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# Check PR is still open
gh pr view {PR} --json state --jq '.state'
```

If the PR is merged or closed, stop and inform the user. No fixes to push.

### Step 1: Fetch all review comments

Two sources of comments exist. Use the correct API for each:

**Inline review comments** (code-level feedback from CodeRabbit, human reviewers):
```bash
gh api repos/$REPO/pulls/{PR}/comments \
  --jq '.[] | {id, user: .user.login, path, line, original_line, in_reply_to_id, body, diff_hunk}'
```

**PR conversation comments** (general discussion):
```bash
gh api repos/$REPO/issues/{PR}/comments \
  --jq '.[] | {id, user: .user.login, body, created_at}'
```

Note: Use `gh api` for both (not `gh pr view --json comments`) to get consistent `.user.login` field names.

### Step 2: Filter to actionable, unaddressed comments

**For inline review comments:**
- Group by thread: comments with `in_reply_to_id` are replies to the comment with that `id`
- Skip any thread where a reply already exists from the PR author — already addressed
- Skip comments from `linear` (linkback bot)
- **CodeRabbit inline comments** (`.user.login == "coderabbitai[bot]"` with a `.path` field) ARE actionable — these are the real code review issues to evaluate
- **Outdated comments** have `.line == null`. Use the `diff_hunk` field to understand what code was discussed, and search the current file for matching context rather than trusting the stale line number

**For PR conversation comments:**
- Skip comments from bots: `linear`, `aws-amplify-us-east-1`
- Skip CodeRabbit summary comments — these start with `<!-- This is an auto-generated comment` or contain `## Walkthrough` / `## Summary by CodeRabbit`
- Skip your own previous comments
- Skip comments that say "No issues found" or are just review summaries with no actionable items
- For remaining comments, check if a later comment from the PR author exists that references the same issue — if so, already addressed

If **0 actionable comments** remain after filtering, post "No new actionable feedback found" on the PR and stop.

### Step 3: Categorize each comment

Read the relevant code for each actionable comment, then weigh the full set together against the rubric below — don't decide in isolation; the right design for one often only becomes clear once you see what else is flagged, plus any known upcoming work mentioned on the PR.

**Design rubric** (verbatim from `plugins/dev-flow/skills/adversarial-review/SKILL.md`'s "The design rubric" — if that copy changes, update this one to match):

> - Best long-term design over short-term tradeoffs; we care about codebase quality and maintainability, not effort or severity.
> - OK to change adjacent code if it gets us to the better design.
> - Before fixing at the point of failure, zoom out one level: if the thing touched is one of a known kind (connectors, handlers, jobs…), put the fix at the shared seam so current and future members inherit it — a per-instance fix the next person must remember to repeat is a latent regression.
> - Prefer correct-by-default seams over designs where each caller must remember a flag, ordering, or manual step.
> - When reusing shared infrastructure, question whether each inherited behavior belongs in the new context — inherited-but-irrelevant behavior is a wart even when harmless.
> - Judge findings together, not in isolation — the best design often only appears when several concerns plus known upcoming work are held at once.
> - Value simplicity; widen the lens only against concrete demand (planned siblings, 2+ instances), never speculation — zooming out finds the right seam, it doesn't add layers.
> - A fix must be worth its complexity: skip super-rare edge cases and race conditions unless the fix is essentially free.
> - Every change must earn its place; if the fix is worse than the wart, leave it.

Categorize each comment against the rubric as:

- **FIX** — The rubric points to a design that's clearly better, including any shared-seam widening, and it's safe to apply automatically. Fix it.
- **SKIP (false positive)** — The reviewer is wrong or misunderstands the code. Explain why.
- **SKIP (not worth it)** — Real issue, but the fix would cost more complexity than the wart it removes, regardless of scope (speculative, rare-edge-case-only, etc). Explain why.
- **SKIP (unrelated pre-existing)** — A different problem, in code neither the PR nor the comment touches. Explain that it's out of scope for this comment.
- **DEFER (ambiguous or has side effects)** — Genuinely unclear which design is better, it needs product/architecture input, or it has side effects beyond what the comment's code shows. Flag for user.
- **DEFER (large blast radius)** — The rubric points to a better design, but the shared-seam fix touches enough call sites or files that it shouldn't be auto-applied. Propose the approach and flag for user approval.

### Step 4: Fix all FIX items

For each FIX item:
1. Make the code change — or confirm it's already covered, if an earlier FIX item's shared-seam fix already reaches this one
2. Track which files were modified

After all fixes, verify and commit:
```bash
# Run any project-specific lint/typecheck if configured
git add <only the specific files that were changed>
git commit -m "fix: address PR review feedback"
git push
```

**Do NOT use `git add -A` or `git add .`** — only stage the specific files modified during this step. Untracked files in the working directory (`.env` files, local configs) must not be committed.

If `git push` fails (branch diverged), pull with rebase first: `git pull --rebase && git push`.

### Step 5: Post responses

Post a **single** `gh pr comment` summarizing all resolutions:

```markdown
### PR feedback addressed

**Fixed:**
- <description of fix 1> (from @reviewer)
- <description of fix 2> (from @reviewer)

**Not fixing:**
- <description> — <reason: false positive / not worth the complexity / unrelated pre-existing> (from @reviewer)

**Deferred — needs your input:**
- <description> — <reason: ambiguous design / side effects / large blast radius>, proposed approach: <approach> (from @reviewer)

Pushed in commit <sha>.

<!-- addressed-comment-ids: 123, 456, 789 -->
```

The HTML comment with addressed IDs enables idempotent re-runs — on subsequent invocations, parse this to skip already-addressed comments.

For inline review comments, also reply directly to each thread:
```bash
# For fixed items:
gh api repos/$REPO/pulls/{PR}/comments/{comment_id}/replies \
  -f body="Fixed in <sha>: <brief description>"

# For skipped items:
gh api repos/$REPO/pulls/{PR}/comments/{comment_id}/replies \
  -f body="Not fixing: <reason>"

# For deferred items:
gh api repos/$REPO/pulls/{PR}/comments/{comment_id}/replies \
  -f body="Deferred: <reason> — flagged for @<pr-author> to decide."
```

## Important rules

- Never make changes that alter user-facing behavior without explicit approval
- Always verify fixes pass lint/typecheck before committing
- If a comment suggests a large refactor, defer rather than attempt it
- CodeRabbit inline comments (with a `path` field) are the actionable ones — CodeRabbit conversation comments (summaries/walkthroughs) are noise
- CodeRabbit "nitpick" severity items can generally be skipped unless they're clearly correct
- CodeRabbit "Major" severity items should be carefully evaluated — they're often real but sometimes false positives
- When the only question is whether a fix is worth doing (not which design is better — that's DEFER (ambiguous or has side effects)), lean toward making the improvement: effort is never the reason to skip it
