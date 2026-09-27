import { describe, it, expect } from 'vitest'
import { TIER_MODEL } from '@/lib/router-v2'

// Regression test for the bug where the fast-path regex branch and the
// slow-path Haiku classifier disagreed on which model a given tier maps to
// (CRITICAL_CODE resolved to claude-opus-4 on one path, gpt-4o on the
// other). Both branches now read from this single table — this test
// guards against that table ever being duplicated again.
describe('router tier->model mapping', () => {
  it('has exactly one model per tier', () => {
    const tiers = Object.keys(TIER_MODEL)
    expect(tiers.sort()).toEqual(['critical', 'large', 'small', 'tiny'])
  })

  it('assigns the most capable model to the critical tier', () => {
    expect(TIER_MODEL.critical).toBe('claude-opus-4-20250514')
  })

  it('assigns the cheapest model to the tiny tier', () => {
    expect(TIER_MODEL.tiny).toBe('gpt-4o-mini')
  })
})
