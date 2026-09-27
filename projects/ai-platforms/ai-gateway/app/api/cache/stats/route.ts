import {
  redis,
} from '@/lib/redis'
import {
  computeCost,
} from '@/lib/pricing'
import {
  getEnv,
} from '@/lib/env'

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

export async function GET(req: Request) {
  if (!isAuthorized(req)) {
    return new Response(
      'Unauthorized',
      { status: 401 }
    )
  }

  const [
    hits,
    misses,
    tier1Hits,
    tier2Hits,
  ] = await Promise.all([
    redis.get<number>(
      'stats:cache_hits'
    ),
    redis.get<number>(
      'stats:cache_misses'
    ),
    redis.get<number>(
      'stats:cache_hits:tier:1'
    ),
    redis.get<number>(
      'stats:cache_hits:tier:2'
    ),
  ])

  const totalHits = hits ?? 0
  const totalMisses = misses ?? 0

  const total =
    totalHits + totalMisses

  const hitRate =
    total > 0
      ? (totalHits / total) * 100
      : 0

  const tierNames = [
    'tiny',
    'small',
    'large',
    'critical',
  ] as const

  const tierCounts =
    await Promise.all(
      tierNames.map(
        async (tier) => ({
          tier,
          count:
            (await redis.get<number>(
              `stats:tier:${tier}`
            )) ?? 0,
        })
      )
    )

  const tierTotal =
    tierCounts.reduce(
      (sum, item) =>
        sum + item.count,
      0
    )

  const tierBreakdown =
    Object.fromEntries(
      tierCounts.map(
        ({ tier, count }) => [
          tier,
          tierTotal > 0
            ? `${(
                (count /
                  tierTotal) *
                100
              ).toFixed(1)}%`
            : '0%',
        ]
      )
    )

  const [
    totalPromptTokens,
    tokenSampleCount,
    samplesRaw,
  ] = await Promise.all([
    redis.get<number>(
      'stats:total_prompt_tokens'
    ),
    redis.get<number>(
      'stats:token_sample_count'
    ),
    redis.lrange<
      string | number
    >(
      'stats:latency_samples',
      0,
      -1
    ),
  ])

  const samples =
    samplesRaw
      .map(Number)
      .filter(Number.isFinite)
      .sort(
        (a, b) => a - b
      )

  const p95 =
    samples.length > 0
      ? samples[
          Math.min(
            samples.length - 1,
            Math.ceil(
              samples.length *
                0.95
            ) - 1
          )
        ]
      : null

  const avgInputTokens =
    tokenSampleCount &&
    tokenSampleCount > 0
      ? totalPromptTokens! /
        tokenSampleCount
      : null

  /**
   * We deliberately don't fabricate a cost estimate
   * when we have no token samples.
   */
  let estimatedCostSaved = 0

  if (avgInputTokens !== null) {
    const pricing = {
      tiny: 'gpt-4o-mini',
      small:
        'claude-3-5-haiku-20241022',
      large:
        'claude-sonnet-4-20250514',
      critical:
        'claude-opus-4-20250514',
    } as const

    for (const item of tierCounts) {
      const modelId =
        pricing[item.tier]

      const estimatedCost =
        computeCost(
          modelId,
          avgInputTokens,
          0
        )

      estimatedCostSaved +=
        item.count *
        estimatedCost
    }
  }

  return Response.json({
    cache: {
      hitRate:
        `${hitRate.toFixed(1)}%`,
      hits: totalHits,
      misses: totalMisses,
      exactHits: tier1Hits ?? 0,
      semanticHits: tier2Hits ?? 0,
    },

    cost: {
      estimatedSaved:
        avgInputTokens === null
          ? null
          : `$${estimatedCostSaved.toFixed(
              2
            )}`,
      avgInputTokens,
    },

    latency: {
      p95TtftMs: p95,
      sampleCount:
        samples.length,
    },

    routing: {
      tierBreakdown,
    },
  })
}