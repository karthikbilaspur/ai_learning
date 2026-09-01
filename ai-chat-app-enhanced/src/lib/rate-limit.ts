import { env } from "@/lib/env";

type Bucket = { count: number; resetAt: number };
const memory = new Map<string, Bucket>();

type Result = { success: boolean; remaining: number; resetAt: number };

async function memoryLimit(key: string): Promise<Result> {
  const now = Date.now();
  const windowMs = env.RATE_LIMIT_WINDOW_SECONDS * 1000;
  const current = memory.get(key);

  if (!current || now >= current.resetAt) {
    const bucket = { count: 1, resetAt: now + windowMs };
    memory.set(key, bucket);
    return { success: true, remaining: Math.max(0, env.RATE_LIMIT_REQUESTS - 1), resetAt: bucket.resetAt };
  }

  if (current.count >= env.RATE_LIMIT_REQUESTS) {
    return { success: false, remaining: 0, resetAt: current.resetAt };
  }

  current.count += 1;
  return { success: true, remaining: env.RATE_LIMIT_REQUESTS - current.count, resetAt: current.resetAt };
}

export async function rateLimit(key: string): Promise<Result> {
  if (env.UPSTASH_REDIS_REST_URL && env.UPSTASH_REDIS_REST_TOKEN) {
    const url = env.UPSTASH_REDIS_REST_URL;
    const token = env.UPSTASH_REDIS_REST_TOKEN;
    const window = env.RATE_LIMIT_WINDOW_SECONDS;
    const limit = env.RATE_LIMIT_REQUESTS;

    try {
      const res = await fetch(`${url}/pipeline`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify([
          ["INCR", `ai-chat:rate:${key}`],
          ["EXPIRE", `ai-chat:rate:${key}`, window],
        ]),
        cache: "no-store",
      });

      if (!res.ok) throw new Error("Upstash rate limiter failed");
      const data = (await res.json()) as Array<{ result: number }>;
      const count = Number(data?.[0]?.result ?? limit + 1);
      const success = count <= limit;
      return { success, remaining: Math.max(0, limit - count), resetAt: Date.now() + window * 1000 };
    } catch (error) {
      console.error("[RATE_LIMIT_FALLBACK]", error);
    }
  }

  return memoryLimit(key);
}
