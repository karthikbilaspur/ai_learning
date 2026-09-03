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
  const normalized = query.trim()

  if (!normalized || normalized.length < 10 || normalized.length > 500) {
    return false
  }

  if (/\d{6,}/.test(normalized)) {
    return false
  }

  if (normalized.split(/\s+/).length < 3) {
    return false
  }

  return true
}

/**
 * Tenant-scoped cache keys.
 */
export function exactCacheKey(tenantId: string, hash: string) {
  return `exact:${tenantId}:${hash}`
}

export function vectorCacheKey(tenantId: string, cacheId: string) {
  return `cache:${tenantId}:${cacheId}`
}

/**
 * Tenant-scoped popularity.
 *
 * IMPORTANT:
 * Never use one global popularity ZSET for tenant-owned cache entries.
 */
export function popularityKey(tenantId: string) {
  return `cache:popular:${tenantId}`
}

export type CacheEntry = {
  answer: string
  model: string
  query?: string
  createdAt: number
}

/**
 * Cache metrics.
 */
export async function incrCacheHit(tier: 1 | 2) {
  try {
    await Promise.all([
      redis.incr('stats:cache_hits'),
      redis.incr(`stats:cache_hits:tier:${tier}`),
    ])
  } catch {
    // Metrics must never break requests.
  }
}

export async function incrCacheMiss() {
  try {
    await redis.incr('stats:cache_misses')
  } catch {
    // Metrics are best-effort.
  }
}

export async function incrTier(tier: string) {
  try {
    await redis.incr(`stats:tier:${tier}`)
  } catch {
    // Metrics are best-effort.
  }
}

export async function recordLatencySample(ttftMs: number) {
  if (!Number.isFinite(ttftMs) || ttftMs < 0) return

  try {
    await redis.lpush('stats:latency_samples', ttftMs)
    await redis.ltrim('stats:latency_samples', 0, 999)
  } catch {
    // Metrics are best-effort.
  }
}

export async function recordTokenSample(promptTokens: number) {
  if (!Number.isFinite(promptTokens) || promptTokens < 0) return

  try {
    await redis.incrby(
      'stats:total_prompt_tokens',
      Math.round(promptTokens)
    )

    await redis.incr('stats:token_sample_count')
  } catch {
    // Metrics are best-effort.
  }
}