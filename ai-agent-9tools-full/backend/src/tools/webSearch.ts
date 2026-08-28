import { tool } from 'ai';
import { z } from 'zod';

export const webSearchTool = tool({
  description: 'Search the web for current, real-time information, news, facts, docs.',
  parameters: z.object({
    query: z.string().describe('Search query'),
    maxResults: z.number().min(1).max(10).default(5).optional(),
  }),
  execute: async ({ query, maxResults = 5 }) => {
    // Using Tavily API - replace with your key. Fallback to DuckDuckGo scraper if needed.
    const TAVILY_KEY = process.env.TAVILY_API_KEY;
    if (!TAVILY_KEY) {
      return { warning: 'TAVILY_API_KEY not set, returning mock', query, results: [{ title: 'Mock Result', content: `Result for ${query}`, url: 'https://example.com' }] };
    }
    const res = await fetch('https://api.tavily.com/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: TAVILY_KEY, query, max_results: maxResults, search_depth: 'advanced' }),
    });
    const data = await res.json();
    return { query, results: data.results };
  },
});
