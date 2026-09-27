import { describe, it, expect } from 'vitest'
import { exactCacheKey, vectorCacheKey } from '@/lib/redis'

// Regression test for the tenant-isolation bug: exact-tier cache keys had
// no tenantId in them while vector-tier keys did, so tenant A could read
// tenant B's cached answer to an identical query.
describe('cache key tenant scoping', () => {
  it('produces different exact-cache keys for different tenants with the same query hash', () => {
    const hash = 'abc123'
    expect(exactCacheKey('tenant-a', hash)).not.toBe(exactCacheKey('tenant-b', hash))
  })

  it('produces different vector-cache keys for different tenants with the same cacheId', () => {
    const cacheId = 'xyz789'
    expect(vectorCacheKey('tenant-a', cacheId)).not.toBe(vectorCacheKey('tenant-b', cacheId))
  })

  it('both key builders include the tenantId as a distinct path segment', () => {
    expect(exactCacheKey('acme', 'h').split(':')).toContain('acme')
    expect(vectorCacheKey('acme', 'id').split(':')).toContain('acme')
  })
})
