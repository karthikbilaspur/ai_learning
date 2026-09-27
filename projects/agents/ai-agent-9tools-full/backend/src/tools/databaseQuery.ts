import { tool } from 'ai';
import { z } from 'zod';

export const databaseQueryTool = tool({
  description: 'Query internal database (users, orders, products). Use for app-specific data. Only SELECT allowed.',
  parameters: z.object({
    table: z.enum(['users', 'orders', 'products', 'logs']).describe('Table to query'),
    query: z.string().describe('SQL WHERE clause or natural language filter, e.g. "status=\"pending\" LIMIT 5"'),
  }),
  execute: async ({ table, query }) => {
    // IMPORTANT: In production, use Drizzle/Prisma with parameterized queries. This is a safe mock.
    if (/drop|delete|update|insert/i.test(query)) {
      return { error: 'Only SELECT queries allowed', table, query };
    }
    // Mock data - replace with db.select().from...
    const mockResults: Record<string, any[]> = {
      users: [{ id: 1, name: 'Kai', email: 'kai@example.com' }],
      orders: [{ id: 101, status: 'pending', total: 299 }],
      products: [{ id: 1, name: 'AI Agent Kit', stock: 50 }],
      logs: [{ id: 1, action: 'tool_call', timestamp: new Date().toISOString() }],
    };
    return { table, filter: query, results: mockResults[table] || [], count: mockResults[table]?.length || 0 };
  },
});
