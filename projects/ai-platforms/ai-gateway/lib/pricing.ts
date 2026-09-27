// Single source of truth for model pricing. Router (pre-call tier
// selection), observability (post-call cost), and stats (cost-saved
// estimate) all import this instead of maintaining their own copies.

export type ModelId =
  | 'gpt-4o-mini'
  | 'claude-3-5-haiku-20241022'
  | 'claude-sonnet-4-20250514'
  | 'gpt-4o'
  | 'claude-opus-4-20250514'

export const MODEL_PRICING: Record<ModelId, { in: number; out: number }> = {
  'gpt-4o-mini': { in: 0.15, out: 0.6 },
  'claude-3-5-haiku-20241022': { in: 0.25, out: 1.25 },
  'claude-sonnet-4-20250514': { in: 3.0, out: 15.0 },
  'gpt-4o': { in: 5.0, out: 15.0 },
  'claude-opus-4-20250514': { in: 15.0, out: 75.0 },
}

export function computeCost(modelId: string, inputTokens: number, outputTokens: number): number {
  const p = MODEL_PRICING[modelId as ModelId] ?? MODEL_PRICING['gpt-4o-mini']
  return (inputTokens / 1e6) * p.in + (outputTokens / 1e6) * p.out
}
