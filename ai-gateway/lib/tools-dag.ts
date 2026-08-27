import { tool } from 'ai'
import { z } from 'zod'
import { redis } from './redis'
import { withResilience } from './circuit-breaker'

async function withToolCache<T>(key: string, ttl: number, fn: () => Promise<T>): Promise<T> {
  try {
    const cached = (await redis.get(key)) as T | null
    if (cached) return cached
  } catch {
    /* cache read failure — fall through to live fetch */
  }
  const result = await fn()
  try {
    await redis.set(key, result, { ex: ttl })
  } catch {
    /* cache write failure is non-fatal */
  }
  return result
}

export type ToolNode = {
  id: string
  execute: (input: any, ctx: Record<string, any>) => Promise<any>
  dependsOn?: string[]
}

// Real topological executor: nodes run once their dependencies have
// resolved; independent nodes at the same level run concurrently. Used by
// lib/tool-graph.ts to pre-resolve known dependency chains (e.g.
// analyzeTrend needs getInternalSales's output) before the model is called,
// rather than the model discovering the dependency itself across two
// separate tool-call round trips.
export async function runDag(nodes: ToolNode[], inputs: Record<string, any>): Promise<Record<string, any>> {
  const results: Record<string, any> = {}
  const remaining = new Map(nodes.map((n) => [n.id, n]))
  const ready = (n: ToolNode) => (n.dependsOn ?? []).every((d) => d in results)

  while (remaining.size > 0) {
    const runnable = [...remaining.values()].filter(ready)
    if (runnable.length === 0) {
      throw new Error(
        `DAG deadlock: unresolved nodes [${[...remaining.keys()].join(', ')}] — check dependsOn for typos or cycles`
      )
    }

    const settled = await Promise.allSettled(
      runnable.map((n) =>
        withResilience(`tool:${n.id}`, () => n.execute(inputs[n.id], results)).then((r) => [n.id, r] as const)
      )
    )

    settled.forEach((outcome, i) => {
      const node = runnable[i]
      if (!node) return // unreachable — i is always a valid index into runnable
      results[node.id] = outcome.status === 'fulfilled' ? outcome.value[1] : { error: String(outcome.reason) }
      remaining.delete(node.id)
    })
  }

  return results
}

export const dagTools = {
  getInternalSales: tool({
    description: 'Get internal sales metrics',
    parameters: z.object({ metric: z.string(), timeframe: z.string() }),
    execute: async ({ metric, timeframe }) =>
      withToolCache(`tool:sales:${metric}:${timeframe}`, 60, () =>
        withResilience('sales-db', async () => ({ metric, value: '12.4% increase', raw: [10, 12, 15, 18] }))
      ),
  }),
  searchCompetitor: tool({
    description: 'Search competitor data via web',
    parameters: z.object({ competitor: z.string() }),
    execute: async ({ competitor }) =>
      withToolCache(`tool:comp:${competitor}`, 3600, () =>
        withResilience('competitor-search', async () => ({ competitor, price: '$49', features: 'similar' }))
      ),
  }),
  analyzeTrend: tool({
    description: 'Analyze trend from sales data — depends on getInternalSales',
    parameters: z.object({ salesData: z.string() }),
    execute: async ({ salesData }) => ({ analysis: `Trend shows ${salesData} growth due to seasonal demand` }),
  }),
  searchDocs: tool({
    description: 'Search internal docs',
    parameters: z.object({ query: z.string() }),
    execute: async ({ query }) =>
      withToolCache(`tool:docs:${query}`, 3600, () =>
        withResilience('docs-search', async () => ({ docs: [`Policy for ${query}: 30 day refund`] }))
      ),
  }),
}
