import { z } from 'zod'

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

  // "key:tenantId,key:tenantId"
  GATEWAY_API_KEYS: z.string().min(1),

  // Used to authenticate internal cron endpoints.
  CACHE_CRON_SECRET: z.string().min(32),
})

export type Env = z.infer<typeof envSchema>

let cached: Env | null = null

export function getEnv(): Env {
  if (cached) return cached

  const parsed = envSchema.safeParse(process.env)

  if (!parsed.success) {
    const issues = parsed.error.issues
      .map((i) => `${i.path.join('.')}: ${i.message}`)
      .join('; ')

    throw new Error(
      `Invalid or missing environment variables — ${issues}`
    )
  }

  cached = parsed.data
  return cached
}