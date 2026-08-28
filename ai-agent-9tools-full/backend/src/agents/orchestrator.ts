import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { allTools } from '../tools';

const SYSTEM_PROMPT = `
You are a helpful AI agent with 9 tools:
- calculator: for math
- web_search: for current info/news
- code_executor: for running JS/Python
- file_reader: for reading uploaded docs
- weather: for weather
- calendar: for checking events/availability
- database_query: for querying app data
- image_generator: for creating images
- memory: for saving/searching long-term memory

Think step by step. Use tools when needed. Explain which tool you used.
`;

export async function runAgent(messages: any[]) {
  const result = streamText({
    model: openai('gpt-4o-mini'),
    system: SYSTEM_PROMPT,
    messages,
    tools: allTools,
    maxSteps: 6,
  });
  return result;
}
