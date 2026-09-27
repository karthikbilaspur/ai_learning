import { tool } from 'ai';
import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

const MEMORY_FILE = path.resolve(process.cwd(), 'data/memory.json');

export const memoryTool = tool({
  description: 'Save or search long-term memory / user preferences. Use to remember facts across chats.',
  parameters: z.object({
    action: z.enum(['save', 'search']).describe('save new memory or search existing'),
    content: z.string().describe('For save: what to remember. For search: query'),
  }),
  execute: async ({ action, content }) => {
    try {
      await fs.mkdir(path.dirname(MEMORY_FILE), { recursive: true });
      let memories: any[] = [];
      try { memories = JSON.parse(await fs.readFile(MEMORY_FILE, 'utf-8')); } catch { memories = []; }

      if (action === 'save') {
        const entry = { id: Date.now(), content, timestamp: new Date().toISOString() };
        memories.push(entry);
        await fs.writeFile(MEMORY_FILE, JSON.stringify(memories, null, 2));
        return { action, saved: entry, totalMemories: memories.length };
      } else {
        // Simple keyword search - upgrade to vector search with Pinecone later
        const results = memories.filter(m => m.content.toLowerCase().includes(content.toLowerCase())).slice(0, 5);
        return { action, query: content, results, totalMemories: memories.length };
      }
    } catch (e: any) {
      return { action, content, error: e.message };
    }
  },
});
