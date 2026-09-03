import { redis } from '@/lib/redis'
import { computeCost, MODEL_PRICING } from '@/lib/pricing'

export async function GET() {
  const [hits, misses] = await Promise.all([
    (redis.get('stats:cache_hit_tier2') as Promise<number | null>).then((v) => v ?? 0),
    (redis.get('stats:cache_miss') as Promise<number | null>).then((v) => v ?? 0),
  ])
  const total = hits + misses
  const hitRate = total ? ((hits / total) * 100).toFixed(1) : '0.0'

  const popular = await redis.zrange('cache:popular', 0, 9, { rev: true, withScores: true })

  const tierCounts = await Promise.all(
    (['tiny', 'small', 'large', 'critical'] as const).map(async (t) => ({
      tier: t,
      count: ((await redis.get(`stats:tier:${t}`)) as number) || 0,
    }))
  )
  const tierTotal = tierCounts.reduce((s, t) => s + t.count, 0)
  const tierBreakdown = Object.fromEntries(
    tierCounts.map((t) => [t.tier, tierTotal ? `${((t.count / tierTotal) * 100).toFixed(0)}%` : '0%'])
  )

  // FIX (portfolio pass): avgInputTokens used to be a hardcoded guess (500).
  // Now derived from a running sum tracked in lib/redis.ts's
  // recordTokenSample, called from onFinish in the chat route.
  const [totalPromptTokens, tokenSampleCount] = await Promise.all([
    (redis.get('stats:total_prompt_tokens') as Promise<number | null>).then((v) => v ?? 0),
    (redis.get('stats:token_sample_count') as Promise<number | null>).then((v) => v ?? 0),
  ])
  const avgInputTokens = tokenSampleCount > 0 ? totalPromptTokens / tokenSampleCount : 500 // fallback until enough samples exist

  const costPerTierHit = Object.fromEntries(
    (['tiny', 'small', 'large', 'critical'] as const).map((t) => {
      const modelId = { tiny: 'gpt-4o-mini', small: 'claude-3-5-haiku-20241022', large: 'claude-sonnet-4-20250514', critical: 'claude-opus-4-20250514' }[t]
      return [t, computeCost(modelId, avgInputTokens, 0)]
    })
  ) as Record<string, number>

  const estimatedCostSaved = tierCounts.reduce((sum, t) => sum + t.count * (costPerTierHit[t.tier] ?? 0), 0)

  // FIX (portfolio pass): p95_latency was a hardcoded { cache: '15ms', llm:
  // '1100ms' } literal. Now computed from the rolling sample list recorded
  // in lib/redis.ts's recordLatencySample.
  const samplesRaw = (await redis.lrange('stats:latency_samples', 0, -1)) as (string | number)[]
  const samples = samplesRaw.map(Number).sort((a, b) => a - b)
  const p95 = samples.length ? samples[Math.floor(samples.length * 0.95)] : null

  return Response.json({
    hitRate: `${hitRate}%`,
    hits,
    misses,
    costSaved: `$${estimatedCostSaved.toFixed(2)}`,
    p95_latency_ttft_ms: p95,
    sample_count: samples.length,
    popularQueries: popular,
    tierBreakdown,
  })
}
