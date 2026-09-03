import {
  vectorIndex,
  redis,
  exactCacheKey,
  vectorCacheKey,
  incrCacheHit,
  incrCacheMiss,
  CacheEntry,
} from './redis'
import { withResilience } from './circuit-breaker'
import { generateObject } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'
import { z } from 'zod'
import OpenAI from 'openai'
import { getEnv } from './env'
import crypto from 'crypto'

const openai = new OpenAI({ apiKey: getEnv().OPENAI_API_KEY })
const THRESHOLD = 0.92
const TTL_SECONDS = 60 * 60 * 24 * 7 // 7 days

async function openaiEmbedding(text: string): Promise<number[]> {
  return withResilience('openai-embedding', async () => {
    const r = await openai.embeddings.create({ model: 'text-embedding-3-small', input: text })
    const first = r.data[0]
    if (!first) throw new Error('Embedding API returned no data')
    return first.embedding
  })
}

async function checkExactCache(query: string, tenantId: string): Promise<CacheEntry | null> {
  const hash = crypto.createHash('sha256').update(query.trim().toLowerCase()).digest('hex')
  const cached = (await redis.get(exactCacheKey(tenantId, hash))) as CacheEntry | null
  if (cached) {
    await redis.zincrby('cache:popular', 1, hash)
    return cached
  }
  return null
}

// Real re-ranking (previously a comment claiming this happened, with no
// call behind it). Vector similarity measures surface closeness, not
// whether the cached answer actually satisfies the new query's intent —
// e.g. "sales last quarter" vs "sales next quarter" embed close but need
// different answers.
const rerankSchema = z.object({ sameIntent: z.boolean(), confidence: z.number().min(0).max(1) })

async function rerankMatch(newQuery: string, cachedQuery: string): Promise<boolean> {
  try {
    const { object } = await withResilience('haiku-rerank', () =>
      generateObject({
        model: anthropic('claude-3-5-haiku-20241022'),
        schema: rerankSchema,
        prompt: `Query A: "${newQuery}"\nQuery B: "${cachedQuery}"\n\nWould the correct answer to Query A also correctly and completely answer Query B (same intent, timeframe, entities)? Be strict.`,
      })
    )
    return object.sameIntent && object.confidence >= 0.7
  } catch {
    return false // fail closed — a miss is safer than a wrong cached answer
  }
}

export async function checkSemanticCacheV2(query: string, tenantId: string) {
  const exact = await checkExactCache(query, tenantId)
  if (exact) {
    await incrCacheHit()
    return { hit: true as const, tier: 1, answer: exact.answer, score: 1.0, model: exact.model }
  }

  let embedding: number[]
  try {
    embedding = await openaiEmbedding(query)
  } catch {
    await incrCacheMiss()
    return { hit: false as const, degraded: true }
  }

  const results = await withResilience('vector-query', () =>
    vectorIndex.query({ vector: embedding, topK: 3, includeMetadata: true })
  )

  if (!results || results.length === 0) {
    await incrCacheMiss()
    return { hit: false as const }
  }

  const top = results[0]
  if (top && top.score > THRESHOLD) {
    const cacheId = top.metadata?.cacheId as string
    const cachedQuery = (top.metadata?.query as string) ?? ''
    const cached = (await redis.get(vectorCacheKey(tenantId, cacheId))) as CacheEntry | null

    if (cached && (await rerankMatch(query, cachedQuery))) {
      await redis.zincrby('cache:popular', 1, cacheId)
      await incrCacheHit()
      return { hit: true as const, tier: 2, answer: cached.answer, score: top.score, model: cached.model }
    }
  }

  await incrCacheMiss()
  return { hit: false as const, score: results[0]?.score ?? 0 }
}

export async function setCacheV2(query: string, answer: string, model: string, tenantId: string) {
  if (answer.length < 50) return
  const hash = crypto.createHash('sha256').update(query.trim().toLowerCase()).digest('hex')
  const cacheId = crypto.randomUUID()
  const entry: CacheEntry = { answer, model, query, createdAt: Date.now() }

  try {
    await redis.set(exactCacheKey(tenantId, hash), entry, { ex: TTL_SECONDS })
    const embedding = await openaiEmbedding(query)
    await vectorIndex.upsert([
      { id: cacheId, vector: embedding, metadata: { cacheId, query: query.slice(0, 200) } },
    ])
    await redis.set(vectorCacheKey(tenantId, cacheId), entry, { ex: TTL_SECONDS })
  } catch {
    // Caching is an optimization; a write failure shouldn't fail the request.
  }
}
