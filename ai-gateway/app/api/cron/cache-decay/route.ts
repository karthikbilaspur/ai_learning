import { redis } from '@/lib/redis'

const EXTEND_THRESHOLD = 10
const DELETE_THRESHOLD = 2
const EXTENDED_TTL = 60 * 60 * 24 * 30
const MIN_AGE_MS = 60 * 60 * 24 * 7 * 1000

// FIX (portfolio pass, round 2): the previous version approximated "age"
// from a key's remaining TTL, which is unreliable — a key can have low TTL
// simply because it's close to its original 7-day expiry, not because it's
// actually old. Cache entries now carry a `createdAt` timestamp (see
// lib/semantic-cache-v2.ts) so age is read directly. Also swapped `KEYS`
// (blocking O(N) scan) for `SCAN` with a cursor, since KEYS is a known
// footgun at any real dataset size on Upstash.
async function scanKeys(pattern: string): Promise<string[]> {
  const found: string[] = []
  let cursor = 0
  do {
    const [next, keys] = await redis.scan(cursor, { match: pattern, count: 100 })
    found.push(...keys)
    cursor = Number(next)
  } while (cursor !== 0)
  return found
}

export async function GET() {
  const popular = (await redis.zrange('cache:popular', 0, -1, { withScores: true })) as (string | number)[]
  const entries: { id: string; score: number }[] = []
  for (let i = 0; i < popular.length; i += 2) {
    entries.push({ id: popular[i] as string, score: Number(popular[i + 1]) })
  }

  let extended = 0
  let deleted = 0
  let skipped = 0

  for (const entry of entries) {
    try {
      const keys = await scanKeys(`*:${entry.id}`)
      if (keys.length === 0) {
        skipped++
        continue
      }

      if (entry.score > EXTEND_THRESHOLD) {
        await Promise.all(keys.map((k) => redis.expire(k, EXTENDED_TTL)))
        extended++
        continue
      }

      if (entry.score < DELETE_THRESHOLD) {
        const values = await Promise.all(keys.map((k) => redis.get(k)))
        const now = Date.now()
        const oldEnough = values.some((v: any) => v?.createdAt && now - v.createdAt > MIN_AGE_MS)
        if (oldEnough) {
          await Promise.all(keys.map((k) => redis.del(k)))
          await redis.zrem('cache:popular', entry.id)
          deleted++
        } else {
          skipped++
        }
        continue
      }

      skipped++
    } catch {
      skipped++
    }
  }

  return Response.json({ processed: entries.length, extended, deleted, skipped })
}
