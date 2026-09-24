# Project 7 — A Deploy Workflow Template

Adds a *manually triggered* deploy workflow. It's intentionally a template
— it doesn't deploy anywhere by itself yet, because there's nowhere to
deploy to until Project 8 provisions a server.

## What's here
- `.github/workflows/deploy.yml` — a `workflow_dispatch` job you trigger by
  hand from the Actions tab; it currently just prints the steps you'd take
- Everything from Project 6

## What to do

1. Push to GitHub, go to **Actions → Deploy to EC2 → Run workflow**, and
   trigger it manually. Read what it prints.
2. Note the comment inside the file about `EC2_HOST`, `EC2_USER`, and
   `EC2_SSH_KEY` — those are GitHub Secrets you'd add once you actually
   have a server (Project 8) to point this at.
3. Think through, on paper, what the real steps would be: SSH into the
   server, pull the latest code, run `docker compose up -d --build`.

## Concepts to know before moving on
- Why deploy workflows are usually manual or gated, unlike CI which runs
  on every push
- What a GitHub Secret is and why credentials never go directly in a
  workflow file

Next: **Project 8 — Infrastructure as Code with Terraform**
