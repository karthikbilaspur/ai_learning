# Project 1 — Linux & Git Basics

Every later project in this series runs on a Linux server and lives in a Git
repo, so this is where it starts.

## What's here
- `scripts/setup-ubuntu.sh` — installs Git, curl, and Docker on a fresh
  Ubuntu machine (you'll reuse this script again in Project 8)
- `.gitignore` — the ignore rules the rest of the projects build on

## What to do

1. Get access to a Linux machine — a spare laptop, a virtual machine, or a
   free-tier cloud VM all work.
2. SSH into it:
   ```bash
   ssh your-user@your-server-ip
   ```
3. Run the setup script:
   ```bash
   bash scripts/setup-ubuntu.sh
   ```
4. Practice basic Git:
   ```bash
   git init
   git checkout -b main
   git add .
   git commit -m "Project 1: Linux and Git basics"
   ```
5. Create a branch, make a small change, and open a pull request against
   `main` if you're pushing this to GitHub. This branch → PR → merge habit
   is the workflow every later project's CI (Project 6) will run against.

## Concepts to know before moving on
- Files, processes, and permissions (`ls -l`, `ps aux`, `chmod`)
- What a port is, and how to check what's listening (`ss -tulpn`)
- `git status`, `git log`, `git branch`, `git diff`

Next: **Project 2 — Python App Basics**
