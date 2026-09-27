# AI Chat App — Enhanced Production Baseline

A stronger version of the supplied Next.js + AI SDK chat starter.

 What was upgraded

 Core requirements

- Streaming OpenAI responses with AI SDK
- Persistent conversation history in PostgreSQL
- Conversation list, selection, creation, and deletion
- Server-side validation with Zod
- Centralized environment validation
- Input/message length limits
- Token-aware context limits
- Model-aware cost estimation
- Persistent assistant usage metadata
- Rate limiting with optional Upstash Redis
- In-process rate-limit fallback for local development
- Safe API error messages
- Markdown + GFM rendering
- Copy / Stop / Regenerate
- System prompt personas

 Production-oriented improvements

- Node runtime for database-backed routes
- Prisma schema and migrations
- No API key exposed to the browser
- Database indexes for conversation/message reads
- Conversation titles generated from the first user message
- Duplicate user-message protection during regeneration
- Explicit build/typecheck/lint scripts
- Configurable limits through environment variables

 Important production note

This is a **production-oriented baseline**, not a claim that security, infrastructure, observability, authentication, or deployment have been universally solved.

Before exposing it to real users, add:

- Authentication and per-user authorization
- CSRF/origin strategy appropriate to your deployment
- Abuse detection and moderation
- Centralized logging/observability (for example Sentry/OpenTelemetry)
- Database backups and migration workflow
- Upstash Redis (or equivalent) in production
- Real model pricing configuration if you change models
- Spend alerts / hard budget controls
- Automated unit/integration/e2e tests
- File scanning if attachments are added

 Setup

 1. Install

```bash
npm install
```

 2.Configure environment

Copy `.env.example` to `.env.local`.

At minimum:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/ai_chat?sslmode=require
```

 3.Create the database schema

For development:

```bash
npm run db:push
```

For a migration-based workflow:

```bash
npm run db:migrate
```

 4.Validate the project

```bash
npm run typecheck
npm run lint
npm run build
```

 5.Run

```bash
npm run dev
```

Open http://localhost:3000.

 Rate limiting

For local development, the app automatically falls back to an in-process limiter.

For production, configure:

```env
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...
```

The Redis path uses a fixed-window counter and the configured request/window limits.

 Token and cost awareness

The server:

1. Estimates context size before sending the request.
2. Rejects oversized contexts.
3. Records provider usage returned by the AI SDK.
4. Calculates an estimated USD cost.
5. Persists usage metadata on assistant messages.

Pricing is configured in `src/lib/tokens.ts`. Treat it as an estimate and update it when changing models/pricing.

 Architecture

```text
Browser
  |
  +-- /api/conversations
  |      |
  |      +-- Prisma --> PostgreSQL
  |
  +-- /api/chat
         |
         +-- Zod validation
         +-- rate limiting
         +-- token/context guard
         +-- AI SDK
         +-- OpenAI
         +-- streaming response
         +-- Prisma --> PostgreSQL
```

 Files worth knowing

- `app/page.tsx` — chat UI and conversation switching
- `app/api/chat/route.ts` — validated streaming chat endpoint
- `app/api/conversations/route.ts` — conversation list/create
- `app/api/conversations/[id]/route.ts` — load/delete conversation
- `src/lib/db.ts` — Prisma client
- `src/lib/rate-limit.ts` — Redis + local rate limiting
- `src/lib/tokens.ts` — token estimation and cost calculation
- `src/lib/env.ts` — environment validation
- `prisma/schema.prisma` — PostgreSQL data model

 Data model

A conversation owns many messages.

Each assistant message stores:

- input token count
- output token count
- estimated cost
- creation timestamp

This makes it straightforward to add a usage dashboard or per-user quotas later.

 Suggested next step

The largest missing product-level feature is **authentication + user ownership**.

Once authentication is added, every conversation should have a `userId`, and every conversation/message query should be authorized against the current user. Do that before treating this as a multi-user SaaS.
