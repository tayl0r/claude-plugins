---
name: address-pr-feedback
description: This skill should be used when the user asks to "address PR comments", "fix PR feedback", "resolve review comments", "handle CodeRabbit comments", "respond to PR reviews", or wants to check a PR for new comments and fix/respond to them. Also trigger when user says "check PR for new comments" or "address feedback on PR".
---

# Address PR Feedback

Fetch all unresolved review comments on a GitHub PR, evaluate each against project and global CLAUDE.md (`~/.claude/CLAUDE.md`) guidance, fix the ones that are clearly better and low-risk, and post a response to every comment explaining what was done or why it was skipped.

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

Read the relevant code for each actionable comment. Then triage the full set together — don't decide comment-by-comment in isolation; the right design for one often only becomes clear once you see what else is flagged, plus any known upcoming work mentioned on the PR.

**Decision framework:**

> Judge by long-term design and maintainability, not effort or severity — never skip a fix because it takes work, and never make one just because it's small. The question is always: does this leave the codebase better, for as many current and future callers as the fix reasonably covers?

Apply, per comment:

1. **Find the right boundary.** If the flagged code is one of a known family (connectors, handlers, jobs, repeated call sites) with 2+ instances that exist today, put the fix at the shared boundary so every member inherits it — a per-instance patch is a latent regression the next person has to remember to repeat. If it's a true one-off, fix it at the point of failure; don't build an abstraction for a single instance or a merely hypothetical sibling.
2. **Prefer correct-by-default.** Between a fix that works automatically and one that requires every caller to remember a flag, an ordering, or a manual step, take the automatic one — even if it means changing adjacent code the PR didn't originally touch. When the fix reuses existing shared infrastructure, drop any inherited behavior that doesn't belong in the new context, even if it's harmless.
3. **Weigh it against the alternative.** A fix must leave the code better than the wart it replaces — skip rare edge cases and race conditions unless closing them is essentially free, and don't take on complexity (new abstraction, wider blast radius) the current findings don't concretely justify.

Categorize each comment as:

- **FIX** — Steps 1-3 land on a design that's clearly better and proportionate, including any shared-boundary widening. Fix it.
- **SKIP (false positive)** — The reviewer is wrong or misunderstands the code. Explain why.
- **SKIP (not worth it)** — Real issue, but the fix would cost more design complexity than the wart it removes (speculative, rare-edge-case-only, etc). Explain why.
- **SKIP (unrelated pre-existing)** — A different problem, in code neither the PR nor the comment touches. Out of scope for this comment.
- **DEFER (ambiguous)** — Genuinely unclear which design is better, or it needs product/architecture input.
- **DEFER (large blast radius)** — The right fix (e.g. a shared-boundary change) touches enough call sites or files that it shouldn't be auto-applied. Propose the shared-boundary approach and flag for user approval.

### Step 4: Fix all FIX items

For each FIX item:
1. Make the code change
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
- <description> — <reason: pre-existing / false positive / needs design input> (from @reviewer)

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
```

## Important rules

- Stay scoped to what each comment actually flags — don't go fix unrelated pre-existing issues nobody raised. Widening a fix to a shared boundary (Step 3) is still in scope even when that touches pre-existing sibling code, because it's addressing the flagged comment, not scope creep.
- Never make changes that alter user-facing behavior without explicit approval
- Always verify fixes pass lint/typecheck before committing
- If a comment suggests a large refactor, defer rather than attempt it
- CodeRabbit inline comments (with a `path` field) are the actionable ones — CodeRabbit conversation comments (summaries/walkthroughs) are noise
- CodeRabbit "nitpick" severity items can generally be skipped unless they're clearly correct
- CodeRabbit "Major" severity items should be carefully evaluated — they're often real but sometimes false positives
- When in doubt about whether a design is better, lean toward making the improvement — effort is never the reason to skip it
