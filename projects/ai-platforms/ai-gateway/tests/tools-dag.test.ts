import { describe, it, expect } from 'vitest'
import { runDag, ToolNode } from '@/lib/tools-dag'

describe('runDag', () => {
  it('runs a dependent node only after its dependency resolves', async () => {
    const order: string[] = []
    const nodes: ToolNode[] = [
      {
        id: 'a',
        execute: async () => {
          order.push('a')
          return { value: 1 }
        },
      },
      {
        id: 'b',
        dependsOn: ['a'],
        execute: async (_input, ctx) => {
          order.push('b')
          expect(ctx.a).toEqual({ value: 1 }) // dependency's result must be visible
          return { value: ctx.a.value + 1 }
        },
      },
    ]

    const results = await runDag(nodes, {})
    expect(order).toEqual(['a', 'b'])
    expect(results.b).toEqual({ value: 2 })
  })

  it('runs independent nodes concurrently (same batch)', async () => {
    const starts: number[] = []
    const nodes: ToolNode[] = ['a', 'b'].map((id) => ({
      id,
      execute: async () => {
        starts.push(Date.now())
        await new Promise((r) => setTimeout(r, 20))
        return id
      },
    }))
    await runDag(nodes, {})
    expect(starts).toHaveLength(2)
    // If run sequentially, second start would be ~20ms after the first.
    expect(Math.abs((starts[0] ?? 0) - (starts[1] ?? 0))).toBeLessThan(10)
  })

  it('throws a clear error on a cyclic graph instead of hanging', async () => {
    const nodes: ToolNode[] = [
      { id: 'a', dependsOn: ['b'], execute: async () => 1 },
      { id: 'b', dependsOn: ['a'], execute: async () => 2 },
    ]
    await expect(runDag(nodes, {})).rejects.toThrow(/deadlock/i)
  })

  it('captures a failing node as an error result without crashing the whole run', async () => {
    const nodes: ToolNode[] = [
      { id: 'a', execute: async () => { throw new Error('boom') } },
    ]
    const results = await runDag(nodes, {})
    expect(results.a.error).toContain('boom')
  })
})
