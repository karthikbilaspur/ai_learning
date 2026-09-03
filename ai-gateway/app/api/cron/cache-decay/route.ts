import { redis, popularityKey } from '@/lib/redis'
import { getEnv } from '@/lib/env'

const EXTEND_THRESHOLD = 10
const DELETE_THRESHOLD = 2

const EXTENDED_TTL =
  60 * 60 * 24 * 30

const MIN_AGE_MS =
  60 * 60 * 24 * 7 * 1000

function isAuthorized(req: Request): boolean {
  const auth =
    req.headers.get('authorization')

  if (!auth?.startsWith('Bearer ')) {
    return false
  }

  const supplied =
    auth.slice('Bearer '.length).trim()

  return supplied ===
    getEnv().CACHE_CRON_SECRET
}

async function scanKeys(
  pattern: string
): Promise<string[]> {
  const found: string[] = []
  let cursor = 0

  do {
    const [next, keys] =
      await redis.scan(cursor, {
        match: pattern,
        count: 100,
      })

    found.push(...keys)
    cursor = Number(next)
  } while (cursor !== 0)

  return found
}

export async function GET(req: Request) {
  if (!isAuthorized(req)) {
    return new Response('Unauthorized', {
      status: 401,
    })
  }

  /**
   * Get tenant IDs from the popularity namespaces.
   *
   * cache:popular:<tenantId>
   */
  const popularityKeys =
    await scanKeys('cache:popular:*')

  let processed = 0
  let extended = 0
  let deleted = 0
  let skipped = 0

  for (const popularityNamespace of popularityKeys) {
    try {
      const tenantId =
        popularityNamespace.slice(
          'cache:popular:'.length
        )

      if (!tenantId) {
        skipped++
        continue
      }

      const popular =
        (await redis.zrange(
          popularityKey(tenantId),
          0,
          -1,
          {
            withScores: true,
          }
        )) as (string | number)[]

      for (
        let i = 0;
        i < popular.length;
        i += 2
      ) {
        const id =
          popular[i] as string

        const score =
          Number(popular[i + 1])

        processed++

        /**
         * Only operate on this tenant's keys.
         */
        const exactKey =
          `exact:${tenantId}:${id}`

        const vectorKey =
          `cache:${tenantId}:${id}`

        const keys = [
          exactKey,
          vectorKey,
        ]

        const existing = []

        for (const key of keys) {
          const value =
            await redis.get(key)

          if (value) {
            existing.push({
              key,
              value: value as {
                createdAt?: number
              },
            })
          }
        }

        if (existing.length === 0) {
          await redis.zrem(
            popularityKey(tenantId),
            id
          )

          skipped++
          continue
        }

        if (score > EXTEND_THRESHOLD) {
          await Promise.all(
            existing.map(({ key }) =>
              redis.expire(
                key,
                EXTENDED_TTL
              )
            )
          )

          extended++
          continue
        }

        if (score < DELETE_THRESHOLD) {
          const now = Date.now()

          const oldEnough =
            existing.some(
              ({ value }) =>
                typeof value.createdAt ===
                  'number' &&
                now - value.createdAt >
                  MIN_AGE_MS
            )

          if (!oldEnough) {
            skipped++
            continue
          }

          await Promise.all(
            existing.map(({ key }) =>
              redis.del(key)
            )
          )

          await redis.zrem(
            popularityKey(tenantId),
            id
          )

          deleted++
          continue
        }

        skipped++
      }
    } catch {
      skipped++
    }
  }

  return Response.json({
    processed,
    extended,
    deleted,
    skipped,
  })
}