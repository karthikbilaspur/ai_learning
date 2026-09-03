import { CircuitState } from 'cockatiel'
import { redis } from '@/lib/redis'
import { allBreakerStates } from '@/lib/circuit-breaker'

// FIX (portfolio pass): circuit breaker states existed but were never
// surfaced anywhere, so the resilience layer was undemonstrable — a
// reviewer or on-call engineer had no way to see whether a dependency was
// currently tripped.
export async function GET() {
  let redisOk = true
  try {
    await redis.ping()
  } catch {
    redisOk = false
  }

  const breakers = allBreakerStates()
  const anyOpen = Object.values(breakers).some((s) => s === CircuitState.Open)

  return Response.json({
    status: redisOk && !anyOpen ? 'ok' : 'degraded',
    redis: redisOk,
    breakers,
    timestamp: new Date().toISOString(),
  })
}
