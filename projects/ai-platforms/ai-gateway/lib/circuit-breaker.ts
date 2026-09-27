import {
  circuitBreaker,
  ConsecutiveBreaker,
  handleAll,
  retry,
  ExponentialBackoff,
  wrap,
  CircuitState,
} from 'cockatiel'

// Real circuit breaker (cockatiel was a listed dependency that nothing used
// before). One breaker per named dependency, so a failing vector index
// doesn't trip the breaker guarding, say, the sales tool.
const breakers = new Map<string, ReturnType<typeof circuitBreaker>>()

function getBreaker(key: string) {
  let b = breakers.get(key)
  if (!b) {
    b = circuitBreaker(handleAll, { halfOpenAfter: 10_000, breaker: new ConsecutiveBreaker(5) })
    breakers.set(key, b)
  }
  return b
}

// Retry (3 attempts, exponential backoff) wrapped INSIDE the breaker, so
// retries count toward the failure threshold instead of masking it.
export function withResilience<T>(key: string, fn: () => Promise<T>): Promise<T> {
  const retryPolicy = retry(handleAll, { maxAttempts: 3, backoff: new ExponentialBackoff() })
  const policy = wrap(retryPolicy, getBreaker(key))
  return policy.execute(() => fn())
}

export function allBreakerStates(): Record<string, CircuitState> {
  const out: Record<string, CircuitState> = {}
  for (const [k, b] of breakers) out[k] = b.state
  return out
}
