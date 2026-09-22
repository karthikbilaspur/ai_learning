# Project 6 — CI with GitHub Actions

Runs Project 3's tests and Project 4's Docker build automatically on every
push, instead of relying on remembering to do it yourself.

## What's here
- `.github/workflows/ci.yml` — installs dependencies, runs `pytest`, builds
  the Docker image
- Everything from Project 5 (app + tests + Docker + Compose + Nginx)

## What to do

1. Push this folder to a new GitHub repository.
2. Go to the **Actions** tab on GitHub and watch the `CI` workflow run on
   your push.
3. Break a test on purpose, push again, and see the workflow fail — then
   fix it and push once more.
4. Open a pull request instead of pushing straight to `main` and watch CI
   run on the PR too.

## Concepts to know before moving on
- What "CI" actually automates here (test + build) vs. what it doesn't
  (it doesn't deploy anywhere — that's Project 7)
- Reading a failed GitHub Actions log to find which step broke

Next: **Project 7 — A Deploy Workflow Template**
