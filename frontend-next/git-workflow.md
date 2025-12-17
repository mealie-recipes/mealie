# Git Workflow & Release Guide

This repository follows a "Fork & Feature" workflow. We maintain three long-running branches:

1. **`mealie-next`**: The exact mirror of the official upstream repo (READ-ONLY).
2. **`dev`**: Integration branch for testing features combined with upstream updates.
3. **`prod`**: Stable branch for the live server.

---

## A. Creating a New Feature Branch

**Rule:** Always branch off `dev`, not main or prod.
**Naming:** Use kebab-case.

1. **Update your local dev branch first:**

   ```bash
   git checkout dev
   git pull origin dev
   ```

2. **Create and switch to your new branch:**

   ```bash
   # Replace 'MEL-X-description' with your ticket/feature name
   git checkout -b MEL-X-description
   ```

3. **Work and Commit:**
   ```bash
   git add .
   git commit -m "feat: added new recipe card"
   ```

---

## B. Merging to Dev (Testing/QA)

Once your feature is working locally, merge it into dev to combine it with other work.

1. **Switch to dev:**

   ```bash
   git checkout dev
   ```

2. **Merge your feature:**

   ```bash
   # Note: If your branch name has special chars like '&', wrap it in quotes!
   git merge MEL-X-description
   ```

3. **Push to GitHub (Origin):**
   ```bash
   git push origin dev
   ```

The `dev` branch is now ready for testing

---

## C. Merging Dev to Prod (Release Day)

_Schedule_: Deployments happen on Mondays (or as needed). This promotes tested code from dev to the live server.

1. **Check what is changing:**

   ```bash
   git log prod..dev --oneline
   ```

2. **Perform the Release:**

   ```bash
   git checkout prod
   git merge dev
   git push origin prod
   ```

---

## Appendix: Keeping Synced with Official Mealie

When the official mealie-next repo releases updates, pull them down the waterfall.

1. **Update the Mirror (mealie-next):**

   ```bash
   git checkout mealie-next
   git fetch upstream
   git reset --hard upstream/mealie-next
   git push origin mealie-next --force
   ```

2. **Update Dev:**

   ```bash
   git checkout dev
   git merge mealie-next
   # Resolve conflicts here if upstream changed files you edited
   git push origin dev
   ```

3. **Dev is now updated** Repeat process to move these updates to Prod.

---
