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

For each actionable comment, read the relevant code and evaluate against the decision framework.

**Decision framework:**

> "Never factor in effort when deciding whether something is worth doing. If the outcome is clearly better and the change is low-risk, just do it. Defer to the user when the fix is ambiguous, has side effects or large blast radius, or needs architecture/design input."

Categorize each comment as:

- **FIX** — The outcome is clearly better and the change is low-risk. Fix it.
- **SKIP (pre-existing)** — The issue exists in code the PR didn't modify. Not our problem.
- **SKIP (false positive)** — The reviewer is wrong or misunderstands the code. Explain why.
- **DEFER (ambiguous)** — The fix is ambiguous, has side effects, or needs design input. Flag for user.
- **DEFER (large blast radius)** — The fix touches many files or changes behavior significantly. Flag for user.

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

- Never fix pre-existing issues that the PR didn't introduce
- Never make changes that alter user-facing behavior without explicit approval
- Always verify fixes pass lint/typecheck before committing
- If a comment suggests a large refactor, defer rather than attempt it
- CodeRabbit inline comments (with a `path` field) are the actionable ones — CodeRabbit conversation comments (summaries/walkthroughs) are noise
- CodeRabbit "nitpick" severity items can generally be skipped unless they're clearly correct
- CodeRabbit "Major" severity items should be carefully evaluated — they're often real but sometimes false positives
- When in doubt about whether to fix or skip, err toward fixing (effort is near-zero)
