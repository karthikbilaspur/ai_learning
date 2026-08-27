import { streamText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

export const runtime = 'edge';

const openai = createOpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
});

const requestCounts = new Map<string, { count: number; timestamp: number }>();

function rateLimit({ key, limit, windowMs }: { key: string; limit: number; windowMs: number }) {
  const now = Date.now();
  const record = requestCounts.get(key);
  
  if (record && now - record.timestamp < windowMs) {
    record.count++;
  } else {
    requestCounts.set(key, { count: 1, timestamp: now });
  }
  
  const current = requestCounts.get(key)!;
  const success = current.count <= limit;
  const remaining = Math.max(0, limit - current.count);
  
  return { success, remaining };
}

export async function POST(req: Request) {
  const ip = req.headers.get('x-forwarded-for')?? 'anon';
  const rl = rateLimit({ key: ip, limit: 10, windowMs: 60_000 });
  if (!rl.success) {
    return new Response(JSON.stringify({ error: 'Rate limited - 10 req/min' }), { status: 429 });
  }

  const { messages } = await req.json();

  const inputTokens = messages.reduce((acc: number, m: { content?: string; parts?: Array<{ text?: string }> }) => acc + countTokens(m.content?? m.parts?.[0]?.text?? ''), 0);
  if (inputTokens > 4000) {
    return new Response(JSON.stringify({ error: `Input too long: ${inputTokens} tokens` }), { status: 413 });
  }

  const result = streamText({
    model: openai(process.env.OPENAI_MODEL || 'gpt-4o-mini'),
    messages,
    onFinish: ({ usage }) => {
      const inputTokens = usage?.inputTokens ?? 0;
      const outputTokens = usage?.outputTokens ?? 0;
      const cost = (inputTokens * 0.00015 + outputTokens * 0.0006) / 1000;
      console.log(`TOKENS: in=${inputTokens} out=${outputTokens} cost=$${cost.toFixed(5)}`);
    },
  });

  return result.toUIMessageStreamResponse({
    headers: {
      'X-Input-Tokens': String(inputTokens),
      'X-RateLimit-Remaining': String(rl.remaining),
    },
  });
}

function countTokens(text: string): number {
    return Math.ceil(text.length / 4);
}
