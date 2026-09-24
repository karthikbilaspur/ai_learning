# Project 3 — Testing the App

Adds automated tests on top of Project 2's app, so you can verify it works
without opening a browser every time — and so Project 6's CI pipeline has
something to run.

## What's here
- `app/main.py` — same app as Project 2
- `tests/test_main.py` — tests for `/`, `/health`, and `/api/info`

## What to do

1. Install dependencies (includes `pytest` and `httpx`):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the tests from this folder:
   ```bash
   pytest -q
   ```
3. Break something on purpose in `app/main.py` (e.g. change the health
   status text) and re-run the tests to see one fail. Fix it, then confirm
   they pass again.

## Concepts to know before moving on
- Why tests are run from the project root, not from inside `tests/`
- The difference between a unit test and a manual check in a browser

Next: **Project 4 — Dockerize the App**
