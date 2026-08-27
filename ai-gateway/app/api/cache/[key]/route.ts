import { redis, exactCacheKey, vectorCacheKey, vectorIndex } from '@/lib/redis'
import { requireAuth } from '@/lib/auth'

// FIX (portfolio pass): the interview talking points claimed cache
// invalidation was "Popularity ZSET + cron decay + manual purge API" — the
// third piece didn't exist. `key` is the cacheId (vector tier) / query hash
// (exact tier) surfaced via /api/cache/stats's popularQueries list.
export async function DELETE(req: Request, { params }: { params: { key: string } }) {
  const auth = requireAuth(req)
  if (auth instanceof Response) return auth
  const { tenantId } = auth
  const { key } = params

  await Promise.allSettled([
    redis.del(exactCacheKey(tenantId, key)),
    redis.del(vectorCacheKey(tenantId, key)),
    redis.zrem('cache:popular', key),
    vectorIndex.delete([key]).catch(() => {}),
  ])

  return Response.json({ purged: key, tenantId })
}
