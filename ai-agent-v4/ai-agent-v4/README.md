# AI Agent V4

Server-side LLM tool calling, a genuine multi-step agent loop, real APIs, Zod validation,
10 tools, one page per tool, execution trace, and no API key in the browser.

Run: `npm install` then copy `.env.example` to `.env`, add `OPENAI_API_KEY`, then `npm run dev:all`.

Frontend: http://localhost:5173 — backend: http://localhost:3001.

Try: "Check Bengaluru weather, find the average engineering salary, and convert that salary from INR to USD."

The agent loop is LLM → tool call → server function/API → tool result → LLM, repeated up to 8 rounds.
The UI shows tool activity but deliberately does not expose private chain-of-thought.

Tools: calculator, dataset search, analytics, weather, currency, time, web search, product lookup,
calendar check, create task.

## What's new in v4

**Restructured code**
- `src/components/` — Header, ToolNav, Console (the shared run UI), TraceView, ConfirmBar.
- `src/pages/` — one file per tool (`Calculator.tsx`, `Weather.tsx`, `Tasks.tsx`, ...), each a thin
  page that renders `<Console tool={...} />` with that tool's metadata. `App.tsx` is now just the
  router and layout shell.
- `src/data/tools.ts` — tool metadata moved out of `App.tsx`.
- `src/lib/api.ts` — the `fetch` calls to the agent API, extracted out of the `Console` component.
- `src/types.ts` — shared `Tool`, `TraceEvent`, `AgentResponse`, etc. types.
- Server and client code was also reformatted (multi-line, consistent style) instead of one giant
  line per file — much easier to read and diff.

**Human-in-the-loop confirmation**
- `create_task` is now a *confirmation-gated* tool (see `requiresConfirmation` in `server/tools.js`).
  When the model wants to call it, the agent loop pauses instead of running it immediately and the
  server responds with `needsConfirmation`, a `sessionId`, and the proposed call.
- The UI (`ConfirmBar.tsx`) shows what the agent wants to do and asks you to Approve or Reject
  before anything happens.
- `POST /api/agent/confirm` resumes the paused loop: on approval it runs the tool and continues; on
  rejection it tells the model the user declined, and the model carries on from there.
- Sessions live in a small in-memory store (`server/sessions.js`) and expire after 10 minutes.
- Known simplification: if a single round contains multiple tool calls and one of them needs
  confirmation, calls after it in that round wait until the round resumes. Good enough for a demo;
  a production version would resolve every call in the round together.

**Persistence**
- Tasks now persist to `data/tasks.json` on disk (`server/tools.js`) instead of living only in a
  runtime array, so they survive a server restart.

**Hardening**
- Fixed a regex bug in the `calculate` tool: the old regex literal `/^[0-9+\\-*/%().\\s]+$/`
  accidentally allowed a stray backslash and the letter "s" through its "arithmetic only" whitelist,
  because `\\-`/`\\s` inside a regex *literal* mean "escaped backslash + literal `-`/`s`", not
  "escaped hyphen" / whitespace shorthand. Now `/^[0-9+\-*/%().\s]+$/`.
- Outbound calls to Open-Meteo, Frankfurter, and DuckDuckGo now time out after 8s
  (`fetchWithTimeout` in `server/tools.js`) instead of potentially hanging a whole agent round.
- CORS is now locked to `FRONTEND_ORIGIN` (default `http://localhost:5173`) instead of allowing any
  origin.
- A small in-memory rate limiter caps `/api/agent` and `/api/agent/confirm` at 20 requests/minute
  per IP, so a single client can't silently burn your OpenAI quota.
- The frontend shows request failures in a dedicated error banner instead of only inline text.

## Still worth doing next
- Swap the in-memory session store and rate limiter for something that survives a restart and works
  across multiple server instances (Redis, or a small database).
- Extend confirmation-gating to any future tool that writes data, sends messages, or spends money.
- Give the agent a short "plan" step before acting, so multi-tool requests are less reactive and it
  can revise course if an early tool result is surprising.
