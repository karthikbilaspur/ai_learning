import { Langfuse } from 'langfuse'
import { getEnv } from './env'
import { computeCost } from './pricing'

const env = getEnv()

export const langfuse = new Langfuse({
  secretKey: env.LANGFUSE_SECRET_KEY,
  publicKey: env.LANGFUSE_PUBLIC_KEY,
  baseUrl: env.LANGFUSE_HOST,
})

export async function traceQuery(data: {
  query: string
  cacheHit: boolean
  tier: string
  modelId: string
  cacheScore?: number
  ttft?: number
  cost?: number
  tenantId: string
  triggeredGraphs?: string[]
}) {
  try {
    langfuse.trace({ name: 'ai-gateway-query', metadata: data, tags: [data.tier, data.cacheHit ? 'cache_hit' : 'cache_miss'] })
    await langfuse.flushAsync() // serverless functions can freeze before the SDK's internal batch flushes on its own
  } catch {
    /* observability must never break the user-facing request */
  }
}

export { computeCost }
