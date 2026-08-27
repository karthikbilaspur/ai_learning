const store = new Map<string, { count: number; resetAt: number }>();

export function rateLimit({ key, limit, windowMs }: { key: string; limit: number; windowMs: number }) {
  const now = Date.now();
  const bucket = store.get(key);
  if (!bucket || now > bucket.resetAt) {
    store.set(key, { count: 1, resetAt: now + windowMs });
    return { success: true, remaining: limit - 1 };
  }
  if (bucket.count >= limit) return { success: false, remaining: 0 };
  bucket.count++;
  return { success: true, remaining: limit - bucket.count };
}