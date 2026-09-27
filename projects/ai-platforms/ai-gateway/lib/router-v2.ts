import { anthropic } from '@ai-sdk/anthropic'
import { generateObject } from 'ai'
import { z } from 'zod'
import { withResilience } from './circuit-breaker'
import { ModelId } from './pricing'

export type Tier = 'tiny' | 'small' | 'large' | 'critical'

const schema = z.object({
  type: z.enum(['SIMPLE_FACTUAL', 'REASONING', 'NEEDS_TOOLS', 'CRITICAL_CODE']),
  confidence: z.number().min(0).max(1),
  reason: z.string(),
  needsTools: z.boolean(),
})

// Single tier->model table. Previously the regex fast-path and the Haiku
// slow-path each hardcoded their own mapping and disagreed for
// CRITICAL_CODE (opus vs gpt-4o) — same classification, different model
// depending on which branch fired.
export const TIER_MODEL: Record<Tier, ModelId> = {
  tiny: 'gpt-4o-mini',
  small: 'claude-3-5-haiku-20241022',
  large: 'claude-sonnet-4-20250514',
  critical: 'claude-opus-4-20250514',
}

const TYPE_TO_TIER: Record<z.infer<typeof schema>['type'], Tier> = {
  SIMPLE_FACTUAL: 'tiny',
  REASONING: 'small',
  NEEDS_TOOLS: 'large',
  CRITICAL_CODE: 'critical',
}

export type RoutingResult = { tier: Tier; modelId: ModelId; meta: Record<string, any> }

export async function routeQueryV2(query: string): Promise<RoutingResult> {
  const q = query.toLowerCase()

  if (q.length < 40 && !q.includes('compare') && !q.includes('analyze') && !q.includes('why')) {
    return { tier: 'tiny', modelId: TIER_MODEL.tiny, meta: { type: 'SIMPLE_FACTUAL', confidence: 0.9 } }
  }
  if (q.includes('code') || q.includes('bug') || q.includes('error') || q.includes('algorithm')) {
    return { tier: 'critical', modelId: TIER_MODEL.critical, meta: { type: 'CRITICAL_CODE', confidence: 0.85 } }
  }
  if (q.includes('compare') || q.includes('sales') || q.includes('search') || q.includes('find')) {
    return { tier: 'large', modelId: TIER_MODEL.large, meta: { type: 'NEEDS_TOOLS', confidence: 0.8 } }
  }

  try {
    const { object } = await withResilience('router-haiku', () =>
      generateObject({
        model: anthropic('claude-3-5-haiku-20241022'),
        schema,
        prompt: `Classify this query: "${query}"\n\n- SIMPLE_FACTUAL: direct lookup\n- REASONING: needs explanation/multi-step thought\n- NEEDS_TOOLS: needs search/db/external data\n- CRITICAL_CODE: code generation, debugging, algorithms\n\nReturn type, confidence, reason, needsTools.`,
      })
    )
    const tier = TYPE_TO_TIER[object.type]
    return { tier, modelId: TIER_MODEL[tier], meta: object }
  } catch {
    return {
      tier: 'small',
      modelId: TIER_MODEL.small,
      meta: { type: 'REASONING', confidence: 0, reason: 'classifier_unavailable_fallback' },
    }
  }
}
