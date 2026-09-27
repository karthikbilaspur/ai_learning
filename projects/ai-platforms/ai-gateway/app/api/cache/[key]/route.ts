import { redis, exactCacheKey, vectorCacheKey, vectorIndex, popularityKey } from '@/lib/redis'
import { requireAuth } from '@/lib/auth'

// Manual purge endpoint - tenant-scoped and auth-gated
export async function DELETE(req: Request, { params }: { params: { key: string } }) {
  const auth = requireAuth(req)
  if (auth instanceof Response) return auth
  const { tenantId } = auth
  const { key } = params

  if (!key || key.length > 200) {
    return Response.json({ error: 'Invalid key' }, { status: 400 })
  }

  await Promise.allSettled([
    redis.del(exactCacheKey(tenantId, key)),
    redis.del(vectorCacheKey(tenantId, key)),
    redis.zrem(popularityKey(tenantId), key),
    vectorIndex.delete([key]).catch(() => {}),
  ])

  return Response.json({ purged: key, tenantId })
}