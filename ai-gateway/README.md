# AI Gateway

Cost-aware LLM gateway: 2-tier semantic cache, 4-way cost-aware router,
dependency-ordered tool execution, per-dependency circuit breakers, and
Langfuse observability.

## Architecture

Request → Auth (API key → tenantId) → Rate limit
        → Pre-resolve known tool dependency chains (real DAG)
        → 2-tier cache check (exact hash → semantic vector + LLM re-rank)
              hit  → unified data-stream response
              miss → 4-way router → streamText w/ pre-resolved context
                   → cache the answer, trace to Langfuse, record stats

## Run it

```bash
npm install
cp .env.example .env.local   # fill in real credentials
npm run dev
npm tet                     # unit tests, no external services required
npm run typecheck
```

Every request needs `Authorization: Bearer <key>` where `<key>` is one of
the `key:tenantId` pairs in `GATEWAY_API_KEYS`. tenantId is never trusted
from the request body — it's resolved server-side from the key so tenants
can't read or pollute each other's cache by passing a different id.

## What's real vs. what's a known simplification

Everything described below actually executes — this section exists because
an earlier draft of this project had comments and unused imports claiming
features that weren't implemented (circuit breaker, LLM re-ranking, DAG
execution, cache decay). Those are now real; see `tests/` for the ones
that are directly testable.

**Real:**

- 2-tier cache: exact-hash tier + vector-similarity tier, both tenant-scoped,
  with a Haiku call re-ranking vector hits before serving them (`lib/semantic-cache-v2.ts`)
- 4-way router with a single tier→model table shared by both the fast
  regex path and the slow LLM-classifier path (`lib/router-v2.ts`)
- Dependency-ordered tool execution: `lib/tools-dag.ts`'s `runDag` does a
  real topological run (concurrent within a level, ordered across levels,
  throws on cycles). `lib/tool-graph.ts` is what actually calls it from the
  request path, pre-resolving known chains like sales→trend-analysis
  before the model is invoked
- Per-dependency circuit breakers via `cockatiel`, retried-then-tripped,
  states exposed at `/api/health` (`lib/circuit-breaker.ts`)
- Cache decay cron reads/writes real TTLs and deletes based on an actual
  `createdAt` timestamp stored per entry, using `SCAN` rather than the
  blocking `KEYS` command (`app/api/cron/cache-decay/route.ts`)
- Manual purge endpoint, tenant-scoped and auth-gated
  (`app/api/cache/[key]/route.ts`)
- Stats endpoint computes `tierBreakdown`, `p95_latency`, and `costSaved`
  from real running counters/samples instead of hardcoded literals
  (`app/api/cache/stats/route.ts`)

**Known simplifications, stated plainly:**

- The tool dependency graph (`lib/tool-graph.ts`) only pre-resolves two
  hand-declared chains (sales→trend). It's a real DAG executor with a small,
  hardcoded set of triggers, not a general planner — extending it means
  adding entries to `graphTriggers`, not a config change.
- `p95_latency` is computed from a capped rolling window (last 1000 TTFT
  samples in a Redis list), not a full histogram — fine for a dashboard,
  not for SLA-grade percentile accuracy.
- `avgInputTokens` in the cost-saved estimate falls back to a rough guess
  (500) until enough real samples accumulate; after that it's a true running
  average.
- Auth is a flat API-key allowlist in an env var, not a real identity
  provider — fine for a portfolio project, not for production multi-tenant
  auth.
- The re-ranker and classifier both fail closed (treated as a cache miss /
  fallback tier) on error, which trades a bit of cost/latency for
  correctness — worth knowing if you're optimizing for hit rate specifically.

## Interview talking points (now backed by code + tests)

- **Why a Bloom-filter-style pre-check before embedding?** Saves an
  embedding API call + latency on queries too short/ID-like to ever hit
  cache. (`isCacheableQuery` in `lib/redis.ts` — it's a heuristic filter,
  not literally a Bloom filter; named accurately in comments.)
- **Why not just `Promise.all` for tools?** Some tools depend on others'
  output (`analyzeTrend` needs `getInternalSales`'s result) — see
  `tests/tools-dag.test.ts` for the dependency-ordering and cycle-detection
  behavior.
- **Why re-rank after vector search?** Vector similarity ≠ answer
  relevance — two queries can embed close together but need different
  answers (different timeframe, different entity). See the re-rank prompt
  in `lib/semantic-cache-v2.ts`.
- **How is cache invalidated?** Popularity ZSET + age-based cron decay
  (real `createdAt` check, not a TTL proxy) + a manual purge API.
- **How is the router evaluated?** `meta.confidence` is logged to Langfuse
  on every routing decision; pairing that with periodic human-labeled
  samples is a next step, not yet automated here.
