import { z } from 'zod'

// FIX (portfolio pass): every client previously read process.env.X! directly,
// so a missing var failed deep inside a Redis/Vector/Langfuse constructor
// with a cryptic error instead of a clear message at the point of use. All
// env access now goes through getEnv(), validated once and cached.

const envSchema = z.object({
  UPSTASH_REDIS_REST_URL: z.string().url(),
  UPSTASH_REDIS_REST_TOKEN: z.string().min(1),
  UPSTASH_VECTOR_REST_URL: z.string().url(),
  UPSTASH_VECTOR_REST_TOKEN: z.string().min(1),
  OPENAI_API_KEY: z.string().min(1),
  ANTHROPIC_API_KEY: z.string().min(1),
  LANGFUSE_SECRET_KEY: z.string().min(1),
  LANGFUSE_PUBLIC_KEY: z.string().min(1),
  LANGFUSE_HOST: z.string().url().default('https://cloud.langfuse.com'),
  // "key:tenantId,key:tenantId" — parsed in lib/auth.ts
  GATEWAY_API_KEYS: z.string().min(1),
})

export type Env = z.infer<typeof envSchema>

let cached: Env | null = null

export function getEnv(): Env {
  if (cached) return cached
  const parsed = envSchema.safeParse(process.env)
  if (!parsed.success) {
    const issues = parsed.error.issues.map((i) => `${i.path.join('.')}: ${i.message}`).join('; ')
    throw new Error(`Invalid or missing environment variables — ${issues}`)
  }
  cached = parsed.data
  return cached
}
