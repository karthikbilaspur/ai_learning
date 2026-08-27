import { Redis } from '@upstash/redis'
import { Index } from '@upstash/vector'
import { Ratelimit } from '@upstash/ratelimit'
import { getEnv } from './env'

const env = getEnv()

export const redis = new Redis({
  url: env.UPSTASH_REDIS_REST_URL,
  token: env.UPSTASH_REDIS_REST_TOKEN,
})

export const vectorIndex = new Index({
  url: env.UPSTASH_VECTOR_REST_URL,
  token: env.UPSTASH_VECTOR_REST_TOKEN,
})

export const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(20, '1 m'),
})

export function isCacheableQuery(query: string): boolean {
  if (!query || query.length < 10 || query.length > 500) return false
  if (/\d{6,}/.test(query)) return false
  if (query.split(' ').length < 3) return false
  return true
}

// Tenant-scoped key builders — both cache tiers go through these so they
// can't drift apart (tier 1 previously had no tenant scoping at all).
export function exactCacheKey(tenantId: string, hash: string) {
  return `exact:${tenantId}:${hash}`
}
export function vectorCacheKey(tenantId: string, cacheId: string) {
  return `cache:${tenantId}:${cacheId}`
}

export type CacheEntry = { answer: string; model: string; query?: string; createdAt: number }

export async function incrCacheHit() {
  try {
    await redis.incr('stats:cache_hit_tier2')
  } catch {
    /* stats are best-effort */
  }
}
export async function incrCacheMiss() {
  try {
    await redis.incr('stats:cache_miss')
  } catch {
    /* best-effort */
  }
}
export async function incrTier(tier: string) {
  try {
    await redis.incr(`stats:tier:${tier}`)
  } catch {
    /* best-effort */
  }
}
export async function recordLatencySample(ttftMs: number) {
  try {
    // Cap the sample list so it can't grow unbounded; keep the most recent
    // 1000 samples for a rolling p95 rather than an all-time average.
    await redis.lpush('stats:latency_samples', ttftMs)
    await redis.ltrim('stats:latency_samples', 0, 999)
  } catch {
    /* best-effort */
  }
}
export async function recordTokenSample(promptTokens: number) {
  try {
    await redis.incrby('stats:total_prompt_tokens', promptTokens)
    await redis.incr('stats:token_sample_count')
  } catch {
    /* best-effort */
  }
}
