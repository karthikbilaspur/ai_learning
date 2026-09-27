import { tool } from 'ai'
import { z } from 'zod'
import { redis } from './redis'
import { withResilience } from './circuit-breaker'

async function withToolCache<T>(key: string, ttl: number, fn: () => Promise<T>): Promise<T> {
  try {
    const cached = (await redis.get(key)) as T | null
    if (cached) return cached
  } catch {}
  const result = await fn()
  try {
    await redis.set(key, result, { ex: ttl })
  } catch {}
  return result
}

export type ToolNode = {
  id: string
  execute: (input: any, ctx: Record<string, any>) => Promise<any>
  dependsOn?: string[]
}

export async function runDag(nodes: ToolNode[], inputs: Record<string, any>): Promise<Record<string, any>> {
  const results: Record<string, any> = {}
  const remaining = new Map(nodes.map((n) => [n.id, n]))
  const failed = new Set<string>()

  const ready = (n: ToolNode) => (n.dependsOn?? []).every((d) => d in results &&!failed.has(d))

  while (remaining.size > 0) {
    const runnable = [...remaining.values()].filter(ready)

    if (runnable.length === 0) {
      const blockedByFailure = [...remaining.values()].every(n =>
        (n.dependsOn?? []).some(d => failed.has(d))
      )
      if (blockedByFailure) {
        for (const id of remaining.keys()) {
          if (!(id in results)) {
            results[id] = { error: `skipped due to failed dependency` }
          }
        }
        break
      }
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
      const node = runnable[i]!
      if (outcome.status === 'fulfilled') {
        results[node.id] = outcome.value[1]
      } else {
        results[node.id] = { error: String(outcome.reason) }
        failed.add(node.id)
      }
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