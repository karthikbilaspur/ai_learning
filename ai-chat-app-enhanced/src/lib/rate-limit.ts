import { env } from "@/lib/env";

type Bucket = {
  count: number;
  resetAt: number;
};

type RateLimitResult = {
  success: boolean;
  remaining: number;
  resetAt: number;
};

const memory = new Map<string, Bucket>();

let lastCleanup = 0;

const CLEANUP_INTERVAL_MS = 60_000;

function cleanupExpiredBuckets(now: number) {
  if (now - lastCleanup < CLEANUP_INTERVAL_MS) {
    return;
  }

  lastCleanup = now;

  for (const [key, bucket] of memory) {
    if (now >= bucket.resetAt) {
      memory.delete(key);
    }
  }
}

async function memoryLimit(
  key: string,
): Promise<RateLimitResult> {
  const now = Date.now();

  cleanupExpiredBuckets(now);

  const windowMs =
    env.RATE_LIMIT_WINDOW_SECONDS * 1000;

  const current = memory.get(key);

  if (!current || now >= current.resetAt) {
    const bucket: Bucket = {
      count: 1,
      resetAt: now + windowMs,
    };

    memory.set(key, bucket);

    return {
      success: true,
      remaining: Math.max(
        0,
        env.RATE_LIMIT_REQUESTS - 1,
      ),
      resetAt: bucket.resetAt,
    };
  }

  if (
    current.count >=
    env.RATE_LIMIT_REQUESTS
  ) {
    return {
      success: false,
      remaining: 0,
      resetAt: current.resetAt,
    };
  }

  current.count += 1;

  return {
    success: true,
    remaining: Math.max(
      0,
      env.RATE_LIMIT_REQUESTS -
        current.count,
    ),
    resetAt: current.resetAt,
  };
}

async function redisLimit(
  key: string,
): Promise<RateLimitResult> {
  const url =
    env.UPSTASH_REDIS_REST_URL;

  const token =
    env.UPSTASH_REDIS_REST_TOKEN;

  const windowSeconds =
    env.RATE_LIMIT_WINDOW_SECONDS;

  const limit =
    env.RATE_LIMIT_REQUESTS;

  const redisKey =
    `ai-chat:rate:${key}`;

  const response = await fetch(
    `${url}/pipeline`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify([
        ["INCR", redisKey],
        [
          "EXPIRE",
          redisKey,
          windowSeconds,
        ],
      ]),
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Upstash returned HTTP ${response.status}`,
    );
  }

  const data =
    (await response.json()) as Array<{
      result?: number;
    }>;

  const count = Number(
    data?.[0]?.result ?? limit + 1,
  );

  const success = count <= limit;

  return {
    success,
    remaining: Math.max(
      0,
      limit - count,
    ),
    resetAt:
      Date.now() +
      windowSeconds * 1000,
  };
}

export async function rateLimit(
  key: string,
): Promise<RateLimitResult> {
  const hasRedis =
    Boolean(
      env.UPSTASH_REDIS_REST_URL &&
        env.UPSTASH_REDIS_REST_TOKEN,
    );

  if (hasRedis) {
    try {
      return await redisLimit(key);
    } catch (error) {
      console.error(
        "[RATE_LIMIT_REDIS_ERROR]",
        error,
      );
    }
  }

  return memoryLimit(key);
}