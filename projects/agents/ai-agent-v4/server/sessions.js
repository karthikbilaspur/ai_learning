// Tiny in-memory store for agent runs that are paused waiting on a human
// confirmation (see requiresConfirmation in tools.js). Good enough for a
// single-instance demo server; a real deployment would use Redis or a DB
// so sessions survive a server restart / work across multiple instances.

const store = new Map();
const TTL_MS = 10 * 60 * 1000; // sessions expire after 10 minutes of inactivity

export function createSession(id, data) {
  store.set(id, { ...data, expiresAt: Date.now() + TTL_MS });
}

export function getSession(id) {
  const session = store.get(id);
  if (!session) return null;
  if (Date.now() > session.expiresAt) {
    store.delete(id);
    return null;
  }
  return session;
}

export function deleteSession(id) {
  store.delete(id);
}

// Sweep expired sessions periodically so the map doesn't grow forever.
setInterval(() => {
  const now = Date.now();
  for (const [id, session] of store) {
    if (now > session.expiresAt) store.delete(id);
  }
}, 60_000).unref();
