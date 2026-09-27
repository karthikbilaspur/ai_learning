import { getEnv } from './env'

// FIX (portfolio pass): previously `tenantId` came straight from the
// request body (`const { tenantId = 'default' } = await req.json()`), so
// once cache keys became tenant-scoped, any caller could read or pollute
// any other tenant's cache just by sending a different tenantId — the
// scoping fix created a new hole. tenantId must now be derived server-side
// from a verified API key.

type AuthResult = { tenantId: string; apiKey: string }

function parseKeys(raw: string): Map<string, string> {
  const map = new Map<string, string>()
  for (const pair of raw.split(',')) {
    const [key, tenantId] = pair.split(':').map((s) => s.trim())
    if (key && tenantId) map.set(key, tenantId)
  }
  return map
}

let keyCache: Map<string, string> | null = null

export function authenticate(req: Request): AuthResult | null {
  const header = req.headers.get('authorization') || ''
  const token = header.startsWith('Bearer ') ? header.slice('Bearer '.length).trim() : null
  if (!token) return null

  if (!keyCache) keyCache = parseKeys(getEnv().GATEWAY_API_KEYS)
  const tenantId = keyCache.get(token)
  if (!tenantId) return null

  return { tenantId, apiKey: token }
}

export function requireAuth(req: Request): AuthResult | Response {
  const result = authenticate(req)
  if (!result) {
    return new Response(JSON.stringify({ error: 'Unauthorized — missing or invalid Bearer token' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    })
  }
  return result
}
