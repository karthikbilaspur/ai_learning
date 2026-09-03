import {
  vectorIndex,
  redis,
  exactCacheKey,
  vectorCacheKey,
  popularityKey,
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
const TTL_SECONDS = 60 * 60 * 24 * 7
const VECTOR_TOP_K = 10

async function openaiEmbedding(text: string): Promise<number[]> {
  return withResilience('openai-embedding', async () => {
    const r = await openai.embeddings.create({ model: 'text-embedding-3-small', input: text })
    const first = r.data[0]
    if (!first) throw new Error('Embedding API returned no data')
    return first.embedding
  })
}

function queryHash(query: string): string {
  return crypto.createHash('sha256').update(query.trim().toLowerCase()).digest('hex')
}

async function checkExactCache(query: string, tenantId: string): Promise<CacheEntry | null> {
  const hash = queryHash(query)
  const cached = (await redis.get(exactCacheKey(tenantId, hash))) as CacheEntry | null
  if (!cached) return null
  await redis.zincrby(popularityKey(tenantId), 1, hash)
  return cached
}

const rerankSchema = z.object({ sameIntent: z.boolean(), confidence: z.number().min(0).max(1) })

async function rerankMatch(newQuery: string, cachedQuery: string): Promise<boolean> {
  try {
    const { object } = await withResilience('haiku-rerank', () =>
      generateObject({
        model: anthropic('claude-3-5-haiku-20241022'),
        schema: rerankSchema,
        prompt: `Query A: "${newQuery}"\nQuery B: "${cachedQuery}"\n\nWould the cached answer for B correctly and completely answer A? Be strict about timeframe, entities, scope.`,
      })
    )
    return object.sameIntent && object.confidence >= 0.7
  } catch {
    return false
  }
}

export async function checkSemanticCacheV2(query: string, tenantId: string) {
  const exact = await checkExactCache(query, tenantId)
  if (exact) {
    await incrCacheHit(1)
    return { hit: true as const, tier: 1, answer: exact.answer, score: 1.0, model: exact.model }
  }

  let embedding: number[]
  try {
    embedding = await openaiEmbedding(query)
  } catch {
    await incrCacheMiss()
    return { hit: false as const, degraded: true }
  }

  let results
  try {
    results = await withResilience('vector-query', () =>
      vectorIndex.query({
        vector: embedding,
        topK: VECTOR_TOP_K,
        includeMetadata: true,
        filter: `tenantId = '${tenantId}'`,
      })
    )
  } catch {
    await incrCacheMiss()
    return { hit: false as const, degraded: true }
  }

  if (!results || results.length === 0) {
    await incrCacheMiss()
    return { hit: false as const }
  }

  for (const candidate of results) {
    if (typeof candidate.score!== 'number' || candidate.score <= THRESHOLD) continue
    const cacheId = candidate.metadata?.cacheId as string
    const cachedQuery = (candidate.metadata?.query as string)?? ''
    if (!cacheId ||!cachedQuery) continue

    const cached = (await redis.get(vectorCacheKey(tenantId, cacheId))) as CacheEntry | null
    if (!cached) continue

    if (await rerankMatch(query, cachedQuery)) {
      await redis.zincrby(popularityKey(tenantId), 1, cacheId)
      await incrCacheHit(2)
      return { hit: true as const, tier: 2, answer: cached.answer, score: candidate.score, model: cached.model }
    }
  }

  await incrCacheMiss()
  return { hit: false as const, score: results[0]?.score?? 0 }
}

export async function setCacheV2(query: string, answer: string, model: string, tenantId: string) {
  if (answer.trim().length < 50) return
  const hash = queryHash(query)
  const cacheId = crypto.randomUUID()
  const entry: CacheEntry = { answer, model, query, createdAt: Date.now() }

  try {
    await redis.set(exactCacheKey(tenantId, hash), entry, { ex: TTL_SECONDS })
    const embedding = await openaiEmbedding(query)
    await vectorIndex.upsert([
      { id: cacheId, vector: embedding, metadata: { cacheId, tenantId, query: query.slice(0, 200) } },
    ])
    await redis.set(vectorCacheKey(tenantId, cacheId), entry, { ex: TTL_SECONDS })
    await redis.zadd(popularityKey(tenantId), { score: 0, member: hash })
    await redis.zadd(popularityKey(tenantId), { score: 0, member: cacheId })
  } catch {
    // caching is best-effort
  }
}