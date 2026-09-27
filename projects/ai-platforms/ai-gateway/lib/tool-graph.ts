import { runDag, ToolNode, dagTools } from './tools-dag'

// FIX (portfolio pass): this is the piece that was missing after the first
// round of fixes. `runDag` existed and was tested, but nothing in the
// request path ever called it — app/api/chat/route.ts still handed
// `dagTools` straight to the Vercel AI SDK's flat tool-calling loop, so the
// `dependsOn` field on ToolNode was declared but never read at runtime.
//
// This module declares known dependency chains and pre-resolves them via
// runDag BEFORE the model is invoked, injecting the results as context. For
// a query like "why did sales grow", that means:
//   1. getInternalSales and analyzeTrend run as a real 2-node DAG here
//   2. results are handed to the model as pre-resolved context
//   3. the model answers directly instead of needing two sequential tool
//      round trips (call sales tool -> wait -> call analyze tool -> wait)
//
// Independent tools without known dependency chains (searchDocs,
// standalone searchCompetitor lookups) are left for the model to call
// on-demand via the normal tool loop — this only front-runs the case where
// order actually matters.

type GraphTrigger = {
  id: string
  predicate: (query: string) => boolean
  nodes: ToolNode[]
  inputs: (query: string) => Record<string, any>
}

const salesTrendNodes: ToolNode[] = [
  {
    id: 'getInternalSales',
    // .execute() on an `ai` SDK tool returns PromiseLike, not Promise —
    // ToolNode.execute expects a real Promise, so wrap it explicitly.
    execute: (input) => Promise.resolve(dagTools.getInternalSales.execute(input, {} as any)),
  },
  {
    id: 'analyzeTrend',
    dependsOn: ['getInternalSales'],
    execute: (_input, ctx) =>
      Promise.resolve(
        dagTools.analyzeTrend.execute({ salesData: JSON.stringify(ctx.getInternalSales) }, {} as any)
      ),
  },
]

const graphTriggers: GraphTrigger[] = [
  {
    id: 'sales-trend',
    predicate: (q) => /\b(sales|revenue)\b/.test(q) && /\b(trend|why|grow|declin|analy)/.test(q),
    nodes: salesTrendNodes,
    inputs: () => ({
      getInternalSales: { metric: 'revenue', timeframe: 'last_quarter' },
      analyzeTrend: {},
    }),
  },
]

export type GraphResolution = { triggeredGraphs: string[]; contextMessage: string | null }

export async function resolveToolGraphs(query: string): Promise<GraphResolution> {
  const q = query.toLowerCase()
  const matched = graphTriggers.filter((g) => g.predicate(q))
  if (matched.length === 0) return { triggeredGraphs: [], contextMessage: null }

  const combined: Record<string, any> = {}
  for (const graph of matched) {
    const results = await runDag(graph.nodes, graph.inputs(q))
    Object.assign(combined, results)
  }

  const contextMessage =
    'The following tool results were already resolved (respecting their dependency order) before you were called. ' +
    'Use them directly — do not re-call the corresponding tools unless you need different parameters:\n' +
    JSON.stringify(combined, null, 2)

  return { triggeredGraphs: matched.map((g) => g.id), contextMessage }
}
