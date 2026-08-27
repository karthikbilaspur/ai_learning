import { streamText, convertToCoreMessages, CoreMessage } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'
import { openai } from '@ai-sdk/openai'
import { checkSemanticCacheV2, setCacheV2 } from '@/lib/semantic-cache-v2'
import { routeQueryV2 } from '@/lib/router-v2'
import { dagTools } from '@/lib/tools-dag'
import { resolveToolGraphs } from '@/lib/tool-graph'
import { traceQuery, computeCost } from '@/lib/observability'
import { ratelimit, isCacheableQuery, incrTier, recordLatencySample, recordTokenSample } from '@/lib/redis'
import { requireAuth } from '@/lib/auth'
import { textToDataStreamResponse } from '@/lib/stream-utils'

export const maxDuration = 30

export async function POST(req: Request) {
  const auth = requireAuth(req)
  if (auth instanceof Response) return auth
  const { tenantId } = auth

  const { messages } = await req.json()
  const lastContent = messages[messages.length - 1]?.content
  const lastQuery =
    typeof lastContent === 'string'
      ? lastContent
      : Array.isArray(lastContent)
      ? lastContent.map((p: any) => p.text ?? '').join(' ')
      : ''

  const ip = req.headers.get('x-forwarded-for') || 'anon'
  const { success } = await ratelimit.limit(`${tenantId}:${ip}`)
  if (!success) return new Response('Rate limited', { status: 429 })

  const start = Date.now()
  let ttft = 0

  // Pre-resolve any known dependency-ordered tool chains (real DAG
  // execution — see lib/tool-graph.ts for why this exists).
  const graph = await resolveToolGraphs(lastQuery)

  if (isCacheableQuery(lastQuery)) {
    const cache = await checkSemanticCacheV2(lastQuery, tenantId)
    if (cache.hit) {
      await traceQuery({
        query: lastQuery,
        cacheHit: true,
        tier: 'cache',
        modelId: cache.model ?? 'unknown',
        cacheScore: cache.score,
        tenantId,
      })
      return textToDataStreamResponse(cache.answer, { 'X-Cache': 'HIT', 'X-Tier': String(cache.tier) })
    }
  }

  const routing = await routeQueryV2(lastQuery)
  incrTier(routing.tier).catch(() => {})

  const model = routing.modelId.includes('claude') ? anthropic(routing.modelId) : openai(routing.modelId)

  const coreMessages = convertToCoreMessages(messages)
  const augmentedMessages: CoreMessage[] = graph.contextMessage
    ? [{ role: 'system', content: graph.contextMessage }, ...coreMessages]
    : coreMessages

  const result = await streamText({
    model,
    messages: augmentedMessages,
    tools: dagTools,
    maxSteps: 4,
    onChunk: () => {
      if (ttft === 0) ttft = Date.now() - start
    },
    onFinish: async ({ text, usage }) => {
      if (text.length > 50) await setCacheV2(lastQuery, text, routing.modelId, tenantId)
      recordLatencySample(ttft).catch(() => {})
      recordTokenSample(usage.promptTokens).catch(() => {})
      const cost = computeCost(routing.modelId, usage.promptTokens, usage.completionTokens)
      await traceQuery({
        query: lastQuery,
        cacheHit: false,
        tier: routing.tier,
        modelId: routing.modelId,
        ttft,
        cost,
        tenantId,
        triggeredGraphs: graph.triggeredGraphs,
      })
    },
  })

  return result.toDataStreamResponse({
    headers: {
      'X-Cache': 'MISS',
      'X-Tier': routing.tier,
      'X-Model': routing.modelId,
      'X-Confidence': String(routing.meta.confidence ?? 0),
      'X-Graphs-Resolved': graph.triggeredGraphs.join(',') || 'none',
    },
  })
}
