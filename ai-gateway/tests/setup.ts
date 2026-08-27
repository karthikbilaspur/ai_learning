// lib/redis.ts and lib/observability.ts validate env vars at module load
// time (see lib/env.ts) — this setup file provides dummy values so unit
// tests can import those modules without needing real credentials. Never
// loaded outside the test runner.
process.env.UPSTASH_REDIS_REST_URL = 'https://example.upstash.io'
process.env.UPSTASH_REDIS_REST_TOKEN = 'test-token'
process.env.UPSTASH_VECTOR_REST_URL = 'https://example-vector.upstash.io'
process.env.UPSTASH_VECTOR_REST_TOKEN = 'test-token'
process.env.OPENAI_API_KEY = 'test-key'
process.env.ANTHROPIC_API_KEY = 'test-key'
process.env.LANGFUSE_SECRET_KEY = 'test-key'
process.env.LANGFUSE_PUBLIC_KEY = 'test-key'
process.env.GATEWAY_API_KEYS = 'test-key:test-tenant'
