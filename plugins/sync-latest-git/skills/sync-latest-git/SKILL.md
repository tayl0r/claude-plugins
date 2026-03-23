---
name: sync-latest-git
description: Use when the user wants to pull latest changes, sync branches, update from origin, fast-forward, merge upstream, "pull main", "update main", "sync", "rebase on main", or get their branch up to date with remote
---

# Sync Latest Git

Update the primary branch from origin and optionally merge/rebase into the current feature branch.

## Workflow

```dot
digraph sync {
  rankdir=TB;
  node [shape=box];

  detect [label="Detect primary branch\n(main/master/dev)"];
  on_primary [label="On primary branch?" shape=diamond];
  fetch_merge [label="git fetch origin\ngit merge --ff-only origin/<primary>"];
  fetch_update [label="git fetch origin <primary>:<primary>\n(updates local branch without checkout)"];
  show [label="Show new commits"];
  on_feature [label="On a feature branch?" shape=diamond];
  ask_merge [label="AskUserQuestion:\nMerge primary into feature?"];
  wants_merge [label="User wants merge?" shape=diamond];
  ask_type [label="AskUserQuestion:\nMerge strategy?"];
  do_merge [label="Merge/rebase primary → feature"];
  show_feature [label="Show new commits\non feature branch"];
  done [label="Done"];

  detect -> on_primary;
  on_primary -> fetch_merge [label="yes"];
  on_primary -> fetch_update [label="no"];
  fetch_merge -> show -> done;
  fetch_update -> show -> on_feature;
  on_feature -> ask_merge [label="yes"];
  on_feature -> done [label="no"];
  ask_merge -> wants_merge;
  wants_merge -> ask_type [label="yes"];
  wants_merge -> done [label="no"];
  ask_type -> do_merge -> show_feature -> done;
}
```

### Step-by-step

1. **Detect primary branch**: Check which of `main`, `master`, or `dev` exists as a local branch tracking a remote. Prefer `main` > `master` > `dev`.

2. **Record starting point**:
   ```bash
   OLD_HEAD=$(git rev-parse <primary>)
   ```

3. **Update the primary branch**:

   **If on the primary branch:**
   ```bash
   git fetch origin
   git merge --ff-only origin/<primary>
   ```

   **If on a feature branch** (do NOT checkout primary):
   ```bash
   git fetch origin <primary>:<primary>
   ```
   This fast-forward updates the local primary branch without switching branches. If it outputs `! [rejected]`, the local branch has diverged — STOP and tell the user.

4. **Show new commits** (subject, author, and date):
   ```bash
   git log --format="%h %s (%an, %ar)" <OLD_HEAD>..<primary>
   ```
   If no output, say "Already up to date."

5. **If on a feature branch**: Ask the user via AskUserQuestion:

   **Question 1**: "Merge `<primary>` into `<feature-branch>`?"
   - Options: Yes (Recommended), No

   **Question 2** (only if yes): "Merge strategy?"
   - Options:
     - Merge commit (Recommended) — `git merge <primary>`
     - Rebase — `git rebase <primary>` (rewrites feature branch history)
     - Fast-forward only — `git merge --ff-only <primary>` (fails if feature has its own commits)

6. **Check for dirty working tree** before merging: if `git status --porcelain` has output, warn the user and suggest stashing or committing first.

7. **Perform the merge/rebase** using the chosen strategy. Record feature HEAD first:
   ```bash
   FEATURE_OLD_HEAD=$(git rev-parse HEAD)
   ```
   If merge conflicts occur, run `git merge --abort` (or `git rebase --abort`), tell the user which files conflicted, and suggest manual resolution.

8. **Show new commits** on the feature branch:
   ```bash
   git log --format="%h %s (%an, %ar)" <FEATURE_OLD_HEAD>..HEAD
   ```

9. **If rebase was used** and the feature branch has a remote tracking branch, force-push to update it:
   ```bash
   git push --force-with-lease
   ```
   Rebase rewrites history, so a force push is required. Use `--force-with-lease` (not `--force`) to avoid overwriting someone else's work.

### Edge cases

- **FF merge fails on primary**: Local primary has diverged from origin. Tell the user and suggest `git pull --rebase` or manual resolution. Do NOT force-push or reset.
- **Dirty working tree**: `fetch <primary>:<primary>` works regardless of working tree state, but merging/rebasing into the feature branch requires clean state. Check before step 7.
- **No remote tracking**: If the primary branch doesn't track a remote, tell the user.
